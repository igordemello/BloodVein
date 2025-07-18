from pygame import *
import sys
from pygame.locals import QUIT
import math
from inimigo import Inimigo
import random

class CaveiraDeFogo(Inimigo):
    def __init__(self, x, y, largura, altura, hp, nome="Caveira de Fogo",velocidade=4, dano=20):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.spritesheet = image.load('./assets/Enemies/FireSkull-Sheet.png').convert_alpha()

        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 16
        self.animation_speed = 0.15

        self.nome = nome

        self.frames_direcoes = {
            'baixo': [self.get_frame(i) for i in range(0, 4)],
            'direita': [self.get_frame(i) for i in range(4, 8)],
            'esquerda': [self.get_frame(i) for i in range(8, 12)],
            'cima': [self.get_frame(i) for i in range(12, 16)],
        }

        self.frames = self.frames_direcoes['baixo']
        self.tipo_colisao = 'voador'

        self.dano_area = self.dano
        self.raio_dano = 60
        self.tempo_ultimo_dano = 0
        self.intervalo_dano = 500

        # Configurações de movimento aleatório
        self.direcao = self.gerar_direcao()
        self.tempo_mudanca_direcao = 2000
        self.ultimo_tempo_mudanca = time.get_ticks()

        # Limites do mapa
        self.limite_x_min = 400
        self.limite_x_max = 1500
        self.limite_y_min = 400
        self.limite_y_max = 800

    def gerar_direcao(self):
        angulo = random.uniform(0, 2 * math.pi)
        return [math.cos(angulo), math.sin(angulo)]

    def get_frame(self, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(self.spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))
    
    def atualizar(self, player_pos, tela):
        now = time.get_ticks()
        if self.esta_atordoado():
            return

        if hasattr(self, 'stun_ativo') and self.stun_ativo:
            self.stun_ativo = False

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

        # Muda direção aleatoriamente a cada X ms
        if now - self.ultimo_tempo_mudanca > self.tempo_mudanca_direcao:
            self.direcao = self.gerar_direcao()
            self.ultimo_tempo_mudanca = now

        # Movimento com direção suavizada
        self.vx = self.direcao[0] * self.velocidade
        self.vy = self.direcao[1] * self.velocidade

        self.x += self.vx
        self.y += self.vy

        rebateu = False
        if self.x < self.limite_x_min or self.x > self.limite_x_max:
            self.direcao[0] *= -1
            rebateu = True
        if self.y < self.limite_y_min or self.y > self.limite_y_max:
            self.direcao[1] *= -1
            rebateu = True
        if rebateu:
            self.vx = self.direcao[0] * self.velocidade
            self.vy = self.direcao[1] * self.velocidade
            self.ultimo_tempo_mudanca = now

        self.x = max(self.limite_x_min, min(self.x, self.limite_x_max))
        self.y = max(self.limite_y_min, min(self.y, self.limite_y_max))
        self.rect.topleft = (round(self.x), round(self.y))

        # Define direção visual com base na movimentação
        if abs(self.vx) > abs(self.vy):
            direcao = 'direita' if self.vx > 0 else 'esquerda'
        else:
            direcao = 'baixo' if self.vy > 0 else 'cima'
        self.frames = self.frames_direcoes[direcao]

        # Dano por proximidade
        player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
        if self.rect.colliderect(player_rect.inflate(self.raio_dano, self.raio_dano)):
            if now - self.tempo_ultimo_dano > self.intervalo_dano:
                if hasattr(self, "dar_dano") and callable(self.dar_dano):
                    self.dar_dano()
                self.tempo_ultimo_dano = now

        self.atualizar_animacao()

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo or len(self.frames) == 0:
            return
        self.desenhar_outline_mouseover(tela, self.hp, self.hp_max)

        offset_x, offset_y = offset
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y

        frame = self.frames[self.frame_index]
        tela.blit(frame, (draw_x, draw_y))

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

            fonte = font.Font("assets/Fontes/alagard.ttf", 24)
            texto = fonte.render(str(self.nome), True, (255, 255, 255))
            texto_rect = texto.get_rect(
                center=(barra_x - 20 + largura_barra / 2, barra_y + 30 + 25))  # 25 = altura/2 da barra
            tela.blit(texto, texto_rect)
