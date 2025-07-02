import pygame
from inimigo import Inimigo
from inimigos.orb import Orb
import math

class MouthOrb(Inimigo):
    def __init__(self, x, y, largura=128, altura=128, hp=300, velocidade=1.5, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.anima_dano = False
        self.inicio_dano = 0
        self.duracao_dano = 500  # ms (aumentado para efeito gradual)
        self.foi_atingido = False
        self.tempo_atingido = 0

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
                "usar_indices": list(range(4)),
                "frames": [],
                "loop": False
            },
            "invocacao": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-SpawnSheet.png").convert_alpha(),
                "total_frames": 4,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(10)),
                "frames": [],
                "loop": False
            }
        }

        self.animacao_atual = "idle"
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.05  # diminuído para deixar mais lento

        self._carregar_todas_animacoes()

        self.tempo_ultimo_ataque = 0
        self.cooldown_ataque = 2000

        self.tempo_ultima_invocacao = 0
        self.cooldown_invocacao = 5000
        self.orbs_instanciados = []
        self.max_orbs = 3

        self.estado = "normal"
        self.iniciou_invocacao_em = 0
        self.tempo_para_invocar = 1500
        self.cooldown_modo_invocacao = 7000
        self.ultima_tentativa_invocacao = 0
        self.ja_invocou = False
        self.executando_ataque = False

    def get_hitbox(self):
        raio = min(self.largura, self.altura) // 2
        centro_x = self.x + self.largura // 2
        centro_y = self.y + self.altura // 2
        return pygame.Rect(centro_x - raio, centro_y - raio, raio * 2, raio * 2)

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
        distancia = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)
        alcance = 100
        if distancia > alcance:
            return False

        now = pygame.time.get_ticks()
        if now - self.tempo_ultimo_ataque >= self.cooldown_ataque:
            self.trocar_animacao("ataque")
            self.tempo_ultimo_ataque = now
            self.executando_ataque = True
            return True
        return False

    def desenhar_barra_vida(self, tela):
        if not self.vivo:
            return

        # barra como a dos Orbs (acima do sprite)
        largura_barra = self.largura
        altura_barra = 8
        x = self.x
        y = self.y - 10
        proporcao = max(self.hp, 0) / self.hp_max
        barra_atual = int(largura_barra * proporcao)

        pygame.draw.rect(tela, (60, 60, 60), (x, y, largura_barra, altura_barra))
        pygame.draw.rect(tela, (255, 0, 0), (x, y, barra_atual, altura_barra))
        pygame.draw.rect(tela, (255, 255, 255), (x, y, largura_barra, altura_barra), 1)

    def instanciar_orb(self, grupo_inimigos, colliders):
        if grupo_inimigos is None:
            return
        if len(self.orbs_instanciados) < self.max_orbs:
            orb_x = self.x + self.largura // 2 - 32
            orb_y = self.y + self.altura
            orb_rect = pygame.Rect(orb_x, orb_y, 64, 64)

            for col in colliders:
                if orb_rect.colliderect(col["rect"]):
                    orb_rect.y = self.y - 64
                    break

            novo_orb = Orb(orb_rect.x, orb_rect.y, 64, 64)
            grupo_inimigos.append(novo_orb)
            self.orbs_instanciados.append(novo_orb)

    def atualizar(self, player_pos, tela, grupo_inimigos=None, colliders=[]):
        if not self.vivo:
            return

        now = pygame.time.get_ticks()

        if self.knockback_time:
            if now - self.knockback_time < self.knockback_duration:
                self.x += self.vx
                self.y += self.vy
                return
            else:
                self.knockback_time = 0
                self.vx = 0
                self.vy = 0

        if self.estado == "normal" and self.animacao_atual not in ["ataque", "invocacao"]:
            super().atualizar(player_pos, tela)

        distancia_fuga_minima = 300

        if self.estado == "normal" and now - self.ultima_tentativa_invocacao > self.cooldown_modo_invocacao:
            self.estado = "invocando"
            self.iniciou_invocacao_em = now
            self.trocar_animacao("invocacao")
            self.ultima_tentativa_invocacao = now
            self.ja_invocou = False

        if self.estado == "invocando":
            dx = self.x - player_pos[0]
            dy = self.y - player_pos[1]
            distancia = math.hypot(dx, dy)

            if distancia < distancia_fuga_minima:
                afastar_x = (dx / distancia) * self.velocidade
                afastar_y = (dy / distancia) * self.velocidade
                self.set_velocidade_x(afastar_x)
                self.set_velocidade_y(afastar_y)
            else:
                self.set_velocidade_x(0)
                self.set_velocidade_y(0)

            if not self.ja_invocou:
                frames = self.animacoes[self.animacao_atual]["frames"]
                loop = self.animacoes[self.animacao_atual].get("loop", True)
                if not loop and self.frame_index >= len(frames) - 1:
                    self.instanciar_orb(grupo_inimigos, colliders)
                    self.estado = "normal"
                    self.trocar_animacao("idle")
                    self.ja_invocou = True
        elif self.estado == "normal":
            distancia = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)
            alcance = 100
            if distancia <= alcance:
                self.set_velocidade_x(0)
                self.set_velocidade_y(0)
                if not self.executando_ataque:
                    if self.iniciar_ataque_corpo_a_corpo(player_pos):
                        rot_rect, _ = self.get_hitbox_ataque(player_pos)
                        player_hitbox = pygame.Rect(player_pos[0], player_pos[1], 64, 64)
                        if rot_rect.colliderect(player_hitbox):
                            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                                self.dar_dano()
            else:
                super().atualizar(player_pos, tela)

        if self.animacao_atual == "ataque":
            if self.animacao_terminou():
                self.executando_ataque = False
                self.trocar_animacao("idle")
        elif self.animacao_atual == "invocacao":
            if self.animacao_terminou() and self.estado == "normal":
                self.trocar_animacao("idle")

        self.atualizar_animacao()
        self.orbs_instanciados = [orb for orb in self.orbs_instanciados if orb.vivo]

    def desenhar(self, tela, player_pos, offset=(0,0)):
        if not self.vivo:
            return
            

        frame = self.animacoes[self.animacao_atual]["frames"][self.frame_index]

        if self.foi_atingido and pygame.time.get_ticks() - self.tempo_atingido < 250:
            frame = frame.copy()
            frame.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)

        tela.blit(frame, (self.x, self.y))
        self.desenhar_barra_vida(tela)
