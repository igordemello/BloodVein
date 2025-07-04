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

    def adicionar_particula_dano(self, x, y, valor):
        cor = (255, 50, 50)
        if valor > 20:
            cor = (255, 215, 0) 

        for _ in range(10): 
            angulo = randint(0, 360)
            velocidade = randint(1, 3)
            self.particulas_dano.append({
                'x': x,
                'y': y,
                'vx': math.cos(angulo) * velocidade,
                'vy': math.sin(angulo) * velocidade,
                'cor': cor,
                'tempo': randint(300, 500),
                'tamanho': randint(2, 5)
            })

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

    def atualizar(self, player_pos, tela):

        now = time.get_ticks()

        if now - self.knockback_time < self.knockback_duration:
            # O knockback ainda está ativo → não atualiza perseguição
            return
        else:
            # Knockback acabou → zera velocidade
            self.knockback_x = 0
            self.knockback_y = 0
            self.set_velocidade_x(0)
            self.set_velocidade_y(0)
        self.old_x = self.x
        self.old_y = self.y
        # inimigo morrendo
        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            self.vx = 0
            self.vy = 0
            self.rect.topleft = (self.x, self.y)
            return

        player_x = player_pos[0]
        player_y = player_pos[1]

        self.vx = 0
        self.vy = 0

        
        if abs(player_x - self.x) > 100:
            self.vx = self.velocidade if player_x > self.x else -self.velocidade
        if abs(player_y - self.y) > 100:
            self.vy = self.velocidade if player_y > self.y else -self.velocidade

        rot_rect, _ = self.get_hitbox_ataque((player_x, player_y))
        player_hitbox = Rect(player_x, player_y, 64, 64)

        if rot_rect.colliderect(player_hitbox):
            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                self.dar_dano()

        self.x, self.y = self.rect.topleft
        self.atualizar_animacao()

        if hasattr(self, 'veneno_ativo') and self.veneno_ativo:
            if now >= self.veneno_proximo_tick and self.veneno_ticks > 0:
                self.hp -= self.veneno_dano_por_tick
                self.veneno_ticks -= 1
                self.veneno_proximo_tick = now + self.veneno_intervalo

                # Inicia animação de hit como feedback visual (opcional)
                self.anima_hit = True
                self.time_last_hit_frame = now

            if self.veneno_ticks <= 0:
                self.veneno_ativo = False
    
    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)

    def aplicar_modificadores(self, elite=False):
       gerenciador = GerenciadorModificadores()
       gerenciador.aplicar_modificadores(self, elite)
