from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import randint
from modificadores_inimigos import *
from screen_shake import screen_shaker


class Inimigo:
    def __init__(self, x, y, largura, altura, hp, velocidade=2, dano=0):
        self.alma_coletada = None
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.velocidade = velocidade

        self.particulas_dano = []

        self.ultimo_dano_tempo = 0
        self.fonte_dano = font.Font('assets/Fontes/KiwiSoda.ttf', 20)

        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_time = 0
        self.knockback_duration = 200

        self.old_x = x
        self.old_y = y

        self.hp = hp
        self.hp_max = hp
        self.modificadorDanoRecebido = 1
        self.vivo = True
        self.dano = dano
        self.ultimo_dano_critico = False
        self.congelado = False

        self.pode_congelar = False
        self.pode_sangramento = False
        self.pode_envenenar = False
        self.pode_critar = False
        self.pode_enfraquecer = False

        self.spritesheet = None
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 1
        self.usar_indices = [0]
        self.frames = []
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.10

        self.vy = 0
        self.vx = 0
        self.dx = 0
        self.dy = 0

        self.rect = self.get_hitbox()

        # Adicionando atributos para animação de hit
        self.anima_hit = False
        self.hit_frame_duration = 2000  # ms
        self.time_last_hit_frame = 0
        self.hit_alpha = 200  # Transparência do efeito de hit (0-255)
        self.hit_color = (255, 0, 0)  # Cor vermelha para o efeito de hit

    def aplicar_efeito_hit(self, frame):
        """Aplica um efeito vermelho temporário ao frame quando o inimigo leva dano"""
        if self.anima_hit:
            now = time.get_ticks()
            if now - self.time_last_hit_frame > self.hit_frame_duration:
                self.anima_hit = False
                return frame

            hit_frame = frame.copy()
            hit_frame.fill(self.hit_color, special_flags=BLEND_MULT)
            hit_frame.set_alpha(self.hit_alpha)
            return hit_frame
        return frame

    def get_velocidade(self):
        return (self.vx, self.vy)

    def set_velocidade_x(self, vx):
        self.vx = vx

    def set_velocidade_y(self, vy):
        self.vy = vy

    def mover_se(self, pode_x, pode_y, dx, dy):
        if pode_x:
            self.rect.x += dx
        if pode_y:
            self.rect.y += dy

        self.x, self.y = self.rect.topleft

    def carregar_sprites(self):
        if self.spritesheet:
            self.frames = [self.get_frame(i) for i in self.usar_indices]

    def get_frame(self, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(self.spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def aplicar_knockback(self, direcao_x, direcao_y, intensidade):
        angulo = math.atan2(direcao_y, direcao_x)
        self.knockback_x = math.cos(angulo) * intensidade
        self.knockback_y = math.sin(angulo) * intensidade
        self.knockback_time = time.get_ticks()

        self.set_velocidade_x(self.knockback_x)
        self.set_velocidade_y(self.knockback_y)

    def envenenar(self, duracao_em_segundos, dano_total):
        self.veneno_dano_por_tick = dano_total // 2
        self.veneno_ticks = 5
        self.veneno_intervalo = (duracao_em_segundos * 1000) // 5
        self.veneno_proximo_tick = time.get_ticks() + self.veneno_intervalo
        self.veneno_ativo = True

    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)

    def aplicar_modificadores(self, elite=False):
        gerenciador = GerenciadorModificadores()
        gerenciador.aplicar_modificadores(self, elite)