from pygame import *
import sys
from pygame.locals import QUIT
import math
from inimigo import Inimigo


class FantasmaGasp(Inimigo):
    def __init__(self, x, y, largura, altura, nome="Fantasma Gasp", hp=100, velocidade=1.5, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.nome = nome

        self.spritesheet_idle = image.load('./assets/Enemies/Ghost-IdleSheet.png').convert_alpha()
        self.spritesheet_attack = image.load('./assets/Enemies/Ghost-AttackSheet.png').convert_alpha()


        self.frame_width = 32
        self.frame_height = 32
        self.animation_speed = 0.15
        self.last_update = time.get_ticks()
        self.frame_index = 0
        self.direction = 0
        self.attacking = False

        # Inicializa frames
        self.frames = {
            'idle': [[], [], [], []],
            'attack': [[], [], [], []]
        }

        self.carregar_sprites()
        self.current_animation = 'idle'
        self.current_frames = self.frames['idle'][self.direction]

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)
        self.hitboxArma = (70, 100)
        self.tipo_colisao = 'voador'

        self.pode_congelar = True
        self.pode_sangramento = True
        self.pode_envenenar = True
        self.pode_critar = True
        self.pode_enfraquecer = True

    def carregar_sprites(self):
        for direction in range(4):
            for frame_num in range(4):
                rect = Rect((direction * 4 + frame_num) * self.frame_width, 0,
                            self.frame_width, self.frame_height)
                frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
                frame.blit(self.spritesheet_idle, (0, 0), rect)
                frame = transform.scale(frame, (self.largura, self.altura))
                self.frames['idle'][direction].append(frame)

        for direction in range(4):
            for frame_num in range(4):
                rect = Rect((direction * 4 + frame_num) * self.frame_width, 0,
                            self.frame_width, self.frame_height)
                frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
                frame.blit(self.spritesheet_attack, (0, 0), rect)
                frame = transform.scale(frame, (self.largura, self.altura))
                self.frames['attack'][direction].append(frame)

    def atualizar_direcao(self, player_pos):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        angle = math.atan2(dy, dx)

        if -math.pi / 4 <= angle < math.pi / 4:
            self.direction = 0  # Direita
        elif math.pi / 4 <= angle < 3 * math.pi / 4:
            self.direction = 1  # Baixo
        elif -3 * math.pi / 4 <= angle < -math.pi / 4:
            self.direction = 2  # Cima
        else:
            self.direction = 3  # Esquerda

    def atualizar_animacao(self):
        now = time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            if len(self.current_frames) > 0:
                self.frame_index = (self.frame_index + 1) % len(self.current_frames)

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        offset_x, offset_y = offset
        self.atualizar_direcao((player_pos[0] + offset_x, player_pos[1] + offset_y))

        draw_x = self.x + offset_x
        draw_y = self.y + offset_y

        if self.current_frames:
            frame = self.current_frames[self.frame_index]
            tela.blit(frame, (draw_x, draw_y))

            

            if self.congelado:
                frozen_sprite = frame.copy()
                frozen_sprite.fill((165, 242, 255, 100), special_flags=BLEND_MULT)
                tela.blit(frozen_sprite, (draw_x, draw_y))

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 2500:
            vida_maxima = getattr(self, "hp_max", 100)
            largura_barra = 100
            porcentagem = max(0, min(self.hp / vida_maxima, 1))
            largura_hp = porcentagem * largura_barra

            draw.rect(tela, (255, 200, 200), (draw_x - 20, draw_y + 70, largura_barra, 5))
            draw.rect(tela, (255, 0, 0), (draw_x - 20, draw_y + 70, largura_hp, 5))
            draw.rect(tela, (255, 255, 255), (draw_x - 20, draw_y + 70, largura_barra, 5), 1)

    def atualizar(self, player_pos, tela, inimigos=None, colliders=None, dt=None):
        now = time.get_ticks()

        # Knockback
        if now - self.knockback_time < self.knockback_duration:
            self.atualizar_animacao()
            return

        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            self.vx = 0
            self.vy = 0
            self.rect.topleft = (self.x, self.y)
            return

        self.atualizar_direcao(player_pos)

        rot_rect, _ = self.get_hitbox_ataque(player_pos)
        player_hitbox = Rect(player_pos[0], player_pos[1], 64, 64)
        self.attacking = rot_rect.colliderect(player_hitbox)

        new_animation = 'attack' if self.attacking else 'idle'
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.frame_index = 0  # Reseta animação ao mudar de estado

        self.current_frames = self.frames[self.current_animation][self.direction]

        # Movimentação
        player_x, player_y = player_pos
        self.vx = 0
        self.vy = 0

        if abs(player_x - self.x) > 100:
            self.vx = self.velocidade if player_x > self.x else -self.velocidade
        if abs(player_y - self.y) > 100:
            self.vy = self.velocidade if player_y > self.y else -self.velocidade

        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        self.atualizar_animacao()

        if self.attacking and hasattr(self, "dar_dano") and callable(self.dar_dano):
            self.dar_dano()

        if hasattr(self, 'veneno_ativo') and self.veneno_ativo:
            if now >= self.veneno_proximo_tick and self.veneno_ticks > 0:
                self.hp -= self.veneno_dano_por_tick
                self.veneno_ticks -= 1
                self.veneno_proximo_tick = now + self.veneno_intervalo


    def get_hitbox_ataque(self, player_pos):
        if not hasattr(self, '_last_angle') or self._last_pos != player_pos:
            player_x, player_y = player_pos
            dx = (player_x + 32) - (self.x + 32)
            dy = (player_y + 32) - (self.y + 32)
            self._last_angle = math.atan2(dy, dx)
            self._last_pos = player_pos

        angulo = self._last_angle
        orb_x = self.x + 32 + math.cos(angulo) * (self.radius + 15)
        orb_y = self.y + 32 + math.sin(angulo) * (self.radius + 15)

        Orb_rect = Rect(0, 0, *(self.orbital_size))
        Orb_rect.center = (orb_x, orb_y)

        orb_surf = Surface(self.hitboxArma, SRCALPHA)
        rot_surf = transform.rotate(orb_surf, -math.degrees(angulo))
        rot_rect = rot_surf.get_rect(center=Orb_rect.center)

        return rot_rect, rot_surf