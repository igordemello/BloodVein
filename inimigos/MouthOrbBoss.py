import pygame
from inimigo import Inimigo
from inimigos.orb import Orb
import random
import time
import math

class MouthOrb(Inimigo):
    def __init__(self, x, y, largura=128, altura=128, hp=300, velocidade=1.5, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.sprite_size = (64, 64)
        self.animacoes = {
            "idle": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-IdleSheet-Sheet2.png").convert_alpha(),
                "total_frames": 12,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(12)),
                "frames": []
            },
            "ataque": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-AttackSheet.png").convert_alpha(),
                "total_frames": 10,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(10)),
                "frames": []
            },
            "invocacao": {
                "spritesheet": pygame.image.load("./assets/Enemies/MouthOrb-SpawnSheet.png").convert_alpha(),
                "total_frames": 4,
                "frame_width": 64,
                "frame_height": 64,
                "usar_indices": list(range(4)),
                "frames": []
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
            self.frame_index = (self.frame_index + 1) % len(frames)

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
        self.instanciar_orb(grupo_inimigos)

        if self.animacao_atual not in ["ataque", "invocacao"]:
            self.trocar_animacao("idle")

        self.atualizar_animacao()

    def desenhar(self, tela, player_pos):
        if self.vivo:
            frame = self.animacoes[self.animacao_atual]["frames"][self.frame_index]
            tela.blit(frame, (self.x, self.y))