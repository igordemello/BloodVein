import pygame
from inimigo import Inimigo
from inimigos.orb import Orb
import random
import time
import math

class MouthOrb(Inimigo):
    def __init__(self, x, y, largura=128, altura=128, hp=300, velocidade=1.5, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
         
        self.anima_dano = False
        self.inicio_dano = 0
        self.duracao_dano = 150  # ms

        self.sprite_size = (64, 64)
        self.animacoes = {
            "idle": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-IdleSheet-Sheet2.png").convert_alpha(),
                "total_frames": 12,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(12)),
                "frames": [],
                "loop": True
            },
            "ataque": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-AttackSheet.png").convert_alpha(),
                "total_frames": 10,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(10)),
                "frames": [],
                "loop": False
            },
            "invocacao": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-SpawnSheet.png").convert_alpha(),
                "total_frames": 4,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(4)),
                "frames": [],
                "loop": False
            }
        }

        self.animacao_atual = "idle"
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.15

        self._carregar_todas_animacoes()

        # controle de ataques
        self.tempo_ultimo_ataque = 0
        self.cooldown_ataque = 2000

        self.tempo_ultima_invocacao = 0
        self.cooldown_invocacao = 5000
        self.orbs_instanciados = []
        self.max_orbs = 3

        self.estado = "normal"  # pode ser "normal" ou "invocando"
        self.iniciou_invocacao_em = 0
        self.tempo_para_invocar = 1500  # ms após começar invocação
        self.cooldown_modo_invocacao = 7000  # ms
        self.ultima_tentativa_invocacao = 0

    def _carregar_todas_animacoes(self):
        for chave, dados in self.animacoes.items():
            frames = []
            for i in dados["usar_indices"]:
                rect = pygame.Rect(i * dados["frame_width"], 0, dados["frame_width"], dados["frame_height"])
                frame = pygame.Surface((dados["frame_width"], dados["frame_height"]), pygame.SRCALPHA)
                frame.blit(dados["spritesheet"], (0, 0), rect)
                frame = pygame.transform.scale(frame, (self.largura, self.altura))
                frames.append(frame)
            dados["frames"] = frames

    def trocar_animacao(self, nova_animacao):
        if self.animacao_atual != nova_animacao:
            self.animacao_atual = nova_animacao
            self.frame_index = 0
            self.frame_time = 0

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            frames = self.animacoes[self.animacao_atual]["frames"]
            loop = self.animacoes[self.animacao_atual].get("loop", True)
        
            if self.frame_index < len(frames) - 1:
                self.frame_index += 1
            elif loop:
                self.frame_index = 0

    def animacao_terminou(self):
        frames = self.animacoes[self.animacao_atual]["frames"]
        return self.frame_index == len(frames) - 1 and self.frame_time >= 0.99
    
    def iniciar_ataque_corpo_a_corpo(self, player_pos):
        distancia = math.hypot((player_pos[0] - self.x), (player_pos[1] - self.y))
        alcance = 100  # ou o valor que considerar como "curto alcance"

        if distancia > alcance:
            return  # muito longe para atacar

        now = pygame.time.get_ticks()
        if now - self.tempo_ultimo_ataque >= self.cooldown_ataque:
            self.trocar_animacao("ataque")
            self.tempo_ultimo_ataque = now
  
            rot_rect, _ = self.get_hitbox_ataque(player_pos)
            player_hitbox = pygame.Rect(player_pos[0], player_pos[1], 64, 64)
            if rot_rect.colliderect(player_hitbox):
                if hasattr(self, "dar_dano") and callable(self.dar_dano):
                    self.dar_dano()

    def desenhar_barra_vida(self, tela):
        if not self.vivo:
            return
        largura_barra = 400
        altura_barra = 20
        x = tela.get_width() // 2 - largura_barra // 2
        y = 20

        proporcao = self.hp / 300  # ajuste se tiver hp variável
        barra_atual = int(largura_barra * proporcao)

        pygame.draw.rect(tela, (60, 60, 60), (x, y, largura_barra, altura_barra))  # fundo
        pygame.draw.rect(tela, (200, 0, 0), (x, y, barra_atual, altura_barra))     # vida
        pygame.draw.rect(tela, (255, 255, 255), (x, y, largura_barra, altura_barra), 2)  # contorno

    def tomar_dano(self, quantidade):
        self.hp -= quantidade
        self.anima_dano = True
        self.inicio_dano = pygame.time.get_ticks()

    def instanciar_orb(self, grupo_inimigos):
        now = pygame.time.get_ticks()
        if grupo_inimigos is None:
            return

        if now - self.tempo_ultima_invocacao >= self.cooldown_invocacao:
            if len(self.orbs_instanciados) < self.max_orbs:
                self.trocar_animacao("invocacao")
                self.tempo_ultima_invocacao = now
                offset_x = random.randint(-100, 100)
                offset_y = random.randint(-100, 100)
                novo_orb = Orb(self.x + offset_x, self.y + offset_y, 32, 32)
                grupo_inimigos.append(novo_orb)
                self.orbs_instanciados.append(novo_orb)

    def atualizar(self, player_pos, tela, grupo_inimigos=None):
        super().atualizar(player_pos, tela)

        if not self.vivo:
            return

        # Atualiza ações e animação
        self.iniciar_ataque_corpo_a_corpo(player_pos)
        now = pygame.time.get_ticks()

        # Entrar em modo invocação
        if self.estado == "normal" and now - self.ultima_tentativa_invocacao > self.cooldown_modo_invocacao:
            self.estado = "invocando"
            self.iniciou_invocacao_em = now
            self.trocar_animacao("invocacao")
            self.ultima_tentativa_invocacao = now

        if self.estado == "invocando":
            # Movimento de afastamento
            dx = self.x - player_pos[0]
            dy = self.y - player_pos[1]
            distancia = math.hypot(dx, dy)
            if distancia < 300:  # tenta manter distância
                self.vx = (dx / distancia) * self.velocidade
                self.vy = (dy / distancia) * self.velocidade
                self.mover_se(True, True, self.vx, self.vy)

            # Instancia um Orb após o tempo de preparação
            if self.animacao_terminou():
                self.instanciar_orb(grupo_inimigos)
                self.estado = "normal"
                self.trocar_animacao("idle")
        else:
            self.iniciar_ataque_corpo_a_corpo(player_pos)

        if self.animacao_atual not in ["ataque", "invocacao"]:
            self.trocar_animacao("idle")

        self.atualizar_animacao()

    def desenhar(self, tela, player_pos):
        if self.vivo:
            frame = self.animacoes[self.animacao_atual]["frames"][self.frame_index]

            if self.anima_dano and pygame.time.get_ticks() - self.inicio_dano < self.duracao_dano:
                mask = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
                mask.fill((255, 0, 0, 100))  # vermelho com transparência
                frame_copy = frame.copy()
                frame_copy.blit(mask, (0, 0))
                tela.blit(frame_copy, (self.x, self.y))
            else:
                self.anima_dano = False
                tela.blit(frame, (self.x, self.y))