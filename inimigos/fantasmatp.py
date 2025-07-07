from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo

class FantasmaTp(Inimigo):
    def __init__(self, x, y, largura=64, altura=64, hp=100, velocidade=1.5, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        # Sprites
        self.sprite_idle = image.load('./assets/Enemies/fantasmaTP_idle.png').convert_alpha()
        self.sprite_run = image.load('./assets/Enemies/fantasmaTP_run.png').convert_alpha()
        self.sprite_ataque = image.load('./assets/Enemies/fantasmaTP_ataque.png').convert_alpha()

        self.frame_width = 32
        self.frame_height = 32
        self.animation_speed = 0.15

        self.frames = {
            'idle': [self.get_frame(self.sprite_idle, i) for i in range(4)],
            'run': [self.get_frame(self.sprite_run, i) for i in range(6)],
            'attack': [self.get_frame(self.sprite_ataque, i) for i in range(5)],
        }

        self.estado = 'idle'
        self.current_frames = self.frames['idle']
        self.frame_index = 0
        self.last_update = time.get_ticks()

        # Estado de ataque
        self.atacando = False
        self.tempo_ataque = 0
        self.duracao_ataque = 500

        # Teleporte após ataque
        self.cooldown_pos_ataque = 700  # tempo parado após ataque
        self.tempo_proximo_teleporte = 0
        self.teleportando = False

        # Limites da sala (ajuste conforme necessário)
        self.limite_x_min = 336
        self.limite_x_max = 1583
        self.limite_y_min = 342
        self.limite_y_max = 920

        self.tipo_colisao = 'voador'

    def get_frame(self, spritesheet, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def atualizar(self, player_pos, tela):
        now = time.get_ticks()

        if now - self.knockback_time < self.knockback_duration:
            self.atualizar_animacao()
            return

        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            return

        if self.teleportando:
            if now >= self.tempo_proximo_teleporte:
                self.teleportar()
                self.teleportando = False
                self.estado = 'idle'
            self.atualizar_animacao()
            return

        # Verifica distância para atacar
        distancia = math.hypot(player_pos[0] - self.x, player_pos[1] - self.y)
        if not self.atacando and distancia <= 64:
            self.atacando = True
            self.tempo_ataque = now
            self.estado = 'attack'
            self.frame_index = 0
            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                self.dar_dano()

        # Se atacando
        if self.atacando:
            if now - self.tempo_ataque >= self.duracao_ataque:
                self.atacando = False
                self.teleportando = True
                self.tempo_proximo_teleporte = now + self.cooldown_pos_ataque
            self.atualizar_animacao()
            return

        # Movimento normal de perseguição
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distancia = math.hypot(dx, dy)

        if distancia != 0:
            self.vx = self.velocidade * dx / distancia
            self.vy = self.velocidade * dy / distancia
        else:
            self.vx = 0
            self.vy = 0

        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (round(self.x), round(self.y))

        self.estado = 'run' if self.vx or self.vy else 'idle'
        self.atualizar_animacao()

    def teleportar(self):
        self.x = random.randint(self.limite_x_min, self.limite_x_max)
        self.y = random.randint(self.limite_y_min, self.limite_y_max)
        self.rect.topleft = (round(self.x), round(self.y))

    def atualizar_animacao(self):
        now = time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.estado])
        self.current_frames = self.frames[self.estado]

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        draw_x = round(self.x) + offset[0]
        draw_y = round(self.y) + offset[1]

        if self.current_frames:
            frame = self.current_frames[self.frame_index]
            tela.blit(frame, (draw_x, draw_y))

            if self.congelado:
                frozen_sprite = frame.copy()
                frozen_sprite.fill((165, 242, 255, 100), special_flags=BLEND_MULT)
                tela.blit(frozen_sprite, (draw_x, draw_y))

        if time.get_ticks() - self.ultimo_dano_tempo < 2500:
            vida_maxima = getattr(self, "hp_max", 100)
            largura_barra = 100
            porcentagem = max(0, min(self.hp / vida_maxima, 1))
            largura_hp = porcentagem * largura_barra

            draw.rect(tela, (255, 200, 200), (draw_x - 20, draw_y + 70, largura_barra, 5))
            draw.rect(tela, (255, 0, 0), (draw_x - 20, draw_y + 70, largura_hp, 5))
            draw.rect(tela, (255, 255, 255), (draw_x - 20, draw_y + 70, largura_barra, 5), 1)
