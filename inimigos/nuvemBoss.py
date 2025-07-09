from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo

class NuvemBoss(Inimigo):
    def __init__(self, x, y, largura=200, altura=200, nome="Nuvem", hp=10000, velocidade=5, dano=70):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.nome = nome
        self.hp = hp
        self.hp_max = hp

        # Spritesheets
        self.sprites = {
            'idle': image.load('./assets/Enemies/nuvem_idle.png').convert_alpha(),
            'run': image.load('./assets/Enemies/nuvem_run.png').convert_alpha(),
            'campo': image.load('./assets/Enemies/nuvem_campo_de_força.png').convert_alpha(),
            'raio': image.load('./assets/Enemies/nuvem_raio.png').convert_alpha(),
        }

        # Frame sizes
        self.frame_sizes = {
            'idle': 100,
            'run': 100,
            'campo': 102,
            'raio': 160,
        }

        # Frame counts
        self.frame_counts = {
            'idle': 4,
            'run': 8,
            'campo': 4,
            'raio': 4,
        }

        self.animation_speed = 0.15
        self.frame_index = 0
        self.last_update = time.get_ticks()

        # Animações separadas
        self.offsets = {}
        self.frames = {key: self.carregar_frames(key) for key in self.sprites}
        self.estado = 'idle'
        self.current_frames = self.frames['idle']

        # Estados de ataque
        self.executando_ataque = False
        self.ataque_atual = None
        self.tempo_ultimo_ataque = 0
        self.cooldown_ataque = 2500
        self.tempo_fim_ataque = 0

        self.rect = self.get_hitbox()
        

        self.tipo_colisao = 'voador'

    def carregar_frames(self, chave):
        spritesheet = self.sprites[chave]
        frame_size = self.frame_sizes[chave]  # pode ser 100, 160, etc.
        frame_count = self.frame_counts[chave]
        frames = []
        offsets = []

        for i in range(frame_count):
            # Frame bruto da spritesheet
            rect = Rect(i * frame_size, 0, frame_size, frame_size)
            frame_surface = Surface((frame_size, frame_size), SRCALPHA)
            frame_surface.blit(spritesheet, (0, 0), rect)

            # Centraliza a nuvem de 100x100 no meio do frame
            offset_x = (frame_size - 100) // 2
            offset_y = (frame_size - 100) // 2
            offsets.append((offset_x, offset_y))

            frames.append(frame_surface)

        self.offsets[chave] = offsets
        return frames

    def escolher_ataque(self):
        return random.choice(['campo', 'raio'])

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


        if self.executando_ataque:
            if now >= self.tempo_fim_ataque:
                self.executando_ataque = False
                self.estado = 'idle'
                self.frame_index = 0 
            self.atualizar_animacao()
            return

        # Verifica se pode atacar
        if now - self.tempo_ultimo_ataque >= self.cooldown_ataque:
            self.ataque_atual = self.escolher_ataque()
            self.estado = self.ataque_atual
            self.frame_index = 0
            self.executando_ataque = True
            self.tempo_fim_ataque = now + 1200
            self.frame_index = 0
            self.tempo_ultimo_ataque = now

            if self.ataque_atual == 'raio':
                player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
                rect_raio = Rect(self.x + 50, self.y + 50, 100, 100)
                if player_rect.colliderect(rect_raio):
                    if hasattr(self, "dar_dano") and callable(self.dar_dano):
                        self.dar_dano()
                
            elif self.ataque_atual == 'campo':
                player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
                rect_raio = Rect(self.x + 50, self.y + 50, 100, 100)
                if player_rect.colliderect(rect_raio):
                    if hasattr(self, "dar_dano") and callable(self.dar_dano):
                        self.dar_dano()

            self.atualizar_animacao()
            return

        # Movimento flutuante básico
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)

        if dist != 0:
            self.vx = self.velocidade * dx / dist
            self.vy = self.velocidade * dy / dist
        else:
            self.vx = 0
            self.vy = 0

        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (round(self.x), round(self.y))

        self.estado = 'run' if self.vx or self.vy else 'idle'
        self.atualizar_animacao()

    def atualizar_animacao(self):
        now = time.get_ticks()
        frames = self.frames.get(self.estado, [])
        if not frames:
            return  # Evita erro

        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.current_frames = frames

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo or len(self.current_frames) == 0:
            return

        if self.frame_index >= len(self.current_frames):
            self.frame_index = 0

        frame = self.current_frames[self.frame_index]
        offset_x_frame, offset_y_frame = self.offsets[self.estado][self.frame_index]

        draw_x = round(self.x) + offset[0] - offset_x_frame
        draw_y = round(self.y) + offset[1] - offset_y_frame

        # Desenha o sprite
        tela.blit(frame, (draw_x, draw_y))


        self.desenhar_barra_boss(tela, tela.get_width())

    def desenhar_barra_boss(self, tela, largura_tela):
        if not self.vivo:
            return

        tempo_apos_dano = time.get_ticks() - self.ultimo_dano_tempo
        if tempo_apos_dano > 4000:
            return  # só exibe a barra por 4 segundos após o dano

        # Configurações da barra
        largura_barra = 600
        altura_barra = 20
        x = (largura_tela - largura_barra) // 2
        y = 225  # margem do topo

        vida_maxima = getattr(self, "hp_max", self.hp)
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = int(porcentagem * largura_barra)

        # Fundo
        draw.rect(tela, (50, 50, 50), (x, y, largura_barra, altura_barra))
        # Vida
        draw.rect(tela, (180, 0, 0), (x, y, largura_hp, altura_barra))
        # Moldura
        draw.rect(tela, (255, 200, 0), (x, y, largura_barra, altura_barra), 2)

        



    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura-100, self.altura-100)
