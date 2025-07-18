from pygame import *
from pygame.locals import QUIT
import math
import random
from pygame import time
from inimigo import Inimigo

class MorcegoPadrao(Inimigo):
    def __init__(self, x, y, largura=64, altura=64, nome="Morcego",hp=80, velocidade=2, dano=15):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.sprites_idle = image.load('./assets/Enemies/morcego_idle.png').convert_alpha()
        self.sprites_voando = image.load('./assets/Enemies/morcego_correr.png').convert_alpha()

        self.frame_width = 27
        self.frame_height = 36
        self.animation_speed = 0.12

        self.nome = nome

        self.frames_idle = [self.get_frame(self.sprites_idle, i) for i in range(4)]
        self.frames_voando = [self.get_frame(self.sprites_voando, i) for i in range(6)]

        self.frames = self.frames_idle
        self.estado = 'idle'

        # Movimento aleatório
        self.direcao = self.gerar_direcao()
        self.tempo_mudanca_direcao = 5000  # ms
        self.ultimo_tempo_mudanca = time.get_ticks()

        # Limites do mapa (ajuste conforme seu mapa real)
        self.limite_x_min = 400
        self.limite_x_max = 1500
        self.limite_y_min = 400
        self.limite_y_max = 800

        # Ataque
        self.raio_ataque = 50
        self.atacando = False
        self.tempo_ataque = 0
        self.duracao_ataque = 400  # ms

        self.tipo_colisao = 'voador'

    def get_frame(self, spritesheet, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def gerar_direcao(self):
        angulo = random.uniform(0, 2 * math.pi)
        return [math.cos(angulo), math.sin(angulo)]

    def atualizar(self, player_pos, tela):
        if self.esta_atordoado():
            return

        if hasattr(self, 'stun_ativo') and self.stun_ativo:
            self.stun_ativo = False
        now = time.get_ticks()

        if now - self.knockback_time < self.knockback_duration:
            return
        else:
            self.knockback_x = 0
            self.knockback_y = 0
            self.set_velocidade_x(0)
            self.set_velocidade_y(0)

        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            self.rect.topleft = (self.x, self.y)
            return

        if self.atacando:
            self.estado = 'atacando'
            if now - self.tempo_ataque > self.duracao_ataque:
                self.atacando = False
        else:
            # Movimento aleatório
            if now - self.ultimo_tempo_mudanca > self.tempo_mudanca_direcao:
                self.direcao = self.gerar_direcao()
                self.ultimo_tempo_mudanca = now

            self.vx = self.direcao[0] * self.velocidade
            self.vy = self.direcao[1] * self.velocidade

            self.x += self.vx
            self.y += self.vy

            # Rebate nos limites
            rebateu = False
            if self.x < self.limite_x_min:
                self.x = self.limite_x_min + 1
                self.direcao[0] = abs(self.direcao[0]) * random.uniform(0.9, 1.1)
                self.direcao[1] += random.uniform(-0.2, 0.2)
                rebateu = True
            elif self.x > self.limite_x_max:
                self.x = self.limite_x_max - 1
                self.direcao[0] = -abs(self.direcao[0]) * random.uniform(0.9, 1.1)
                self.direcao[1] += random.uniform(-0.2, 0.2)
                rebateu = True

            if self.y < self.limite_y_min:
                self.y = self.limite_y_min + 1
                self.direcao[1] = abs(self.direcao[1]) * random.uniform(0.9, 1.1)
                self.direcao[0] += random.uniform(-0.2, 0.2)
                rebateu = True
            elif self.y > self.limite_y_max:
                self.y = self.limite_y_max - 1
                self.direcao[1] = -abs(self.direcao[1]) * random.uniform(0.9, 1.1)
                self.direcao[0] += random.uniform(-0.2, 0.2)
                rebateu = True
            if rebateu:
                self.ultimo_tempo_mudanca = now
                # Normaliza a direção para manter velocidade constante
                mag = math.hypot(self.direcao[0], self.direcao[1])
                if mag > 0:
                    self.direcao[0] /= mag
                    self.direcao[1] /= mag

            self.x = max(self.limite_x_min, min(self.x, self.limite_x_max))
            self.y = max(self.limite_y_min, min(self.y, self.limite_y_max))

            self.estado = 'voando'
            self.frames = self.frames_voando

        self.rect.topleft = (round(self.x), round(self.y))

        # Detectar player
        player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
        if self.rect.colliderect(player_rect.inflate(self.raio_ataque, self.raio_ataque)) and not self.atacando:
            self.atacando = True
            self.tempo_ataque = now
            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                self.dar_dano()

        self.atualizar_animacao()

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo or len(self.frames) == 0:
            return
        self.desenhar_outline_mouseover(tela, self.hp, self.hp_max)

        offset_x, offset_y = offset
        draw_x = round(self.x) + offset_x
        draw_y = round(self.y) + offset_y

        frame = self.frames[self.frame_index]
        tela.blit(frame, (draw_x, draw_y))


        # Barra de vida
        vida_maxima = getattr(self, "hp_max", 100)
        largura_barra = 500
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = porcentagem * largura_barra

        barra_x = 980 - (largura_barra / 2)
        barra_y = 0

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 2500:
            draw.rect(tela, (10, 10, 10), (barra_x - 20, barra_y + 30, largura_barra, 50))
            draw.rect(tela, (150, 0, 0), (barra_x - 20, barra_y + 30, largura_hp, 50))
            draw.rect(tela, (255, 255, 255), (barra_x - 20, barra_y + 30, largura_barra, 50), 1)

            # Desenhar o nome centralizado
            fonte = font.Font("assets/Fontes/alagard.ttf", 24)
            texto = fonte.render(str(self.nome), True, (255, 255, 255))
            texto_rect = texto.get_rect(
                center=(barra_x - 20 + largura_barra / 2, barra_y + 30 + 25))  # 25 = altura/2 da barra
            tela.blit(texto, texto_rect)

