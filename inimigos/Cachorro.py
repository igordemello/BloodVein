from pygame import *
import math
import random
from inimigo import Inimigo
from utils import resource_path

class Cerbero(Inimigo):
    def __init__(self, x, y, largura=192, altura=192, nome="Cérbero", hp=8000, velocidade=0.3, dano=60):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.nome = nome
        self.ehboss = True
        self.tipo_colisao = 'obstaculo'
        self.vivo = True

        # Imagens
        self.sprite_idle = image.load(resource_path('assets/Enemies/atena_andar.png')).convert_alpha()
        self.sprite_run = image.load(resource_path('assets/Enemies/atena_ataque.png')).convert_alpha()
        self.sprite_fogo = image.load(resource_path('assets/Enemies/atena_grito.png')).convert_alpha()
        self.sprite_bola_fogo = image.load(resource_path('assets/Enemies/atena_fogo.png')).convert_alpha()

        self.frame_width = 96
        self.frame_height = 96
        self.animation_speed = 0.15

        self.frames_idle = self.carregar_frames(self.sprite_idle, 4)
        self.frames_run = self.carregar_frames(self.sprite_run, 6)

        self.frames = self.frames_idle
        self.estado = "idle"
        self.frame_index = 0
        self.frame_time = 0

        self.cooldown = 5000
        self.ultimo_ataque = time.get_ticks()
        self.modo = 0  # alterna entre os 3 ataques
        self.subataques_restantes = 0

        self.player = None  # setado na sala
        self.projetis = []

    def carregar_frames(self, spritesheet, num_frames):
        frames = []
        for i in range(num_frames):
            rect = Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
            frame.blit(spritesheet, (0, 0), rect)
            frame = transform.scale(frame, (self.largura, self.altura))
            frames.append(frame)
        return frames

    def trocar_estado(self, novo_estado):
        if self.estado != novo_estado:
            self.estado = novo_estado
            self.frame_index = 0
            self.frame_time = 0
            if novo_estado == "idle":
                self.frames = self.frames_idle
            elif novo_estado == "run":
                self.frames = self.frames_run

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def atualizar(self, player_pos, tela, matriz=None, offset=(0, 0)):
        if not self.vivo:
            return

        self.trocar_estado("run")
        self.atualizar_animacao()

        now = time.get_ticks()

        # Se estiver executando subataque (bola de fogo)
        if self.subataques_restantes > 0:
            if now - self.ultimo_ataque >= 500:
                self._atacar_bolas_teleguiadas()
                self.subataques_restantes -= 1
                self.ultimo_ataque = now
            return

        # Se em cooldown
        if now - self.ultimo_ataque < self.cooldown:
            self._seguir_jogador(player_pos)
            return

        # Executa ataque dependendo do modo
        if self.modo == 0:
            self._ataque_fogo_lateral(player_pos)
        elif self.modo == 1:
            self._ataque_grito()
        elif self.modo == 2:
            self.subataques_restantes = 3
        self.modo = (self.modo + 1) % 3
        self.ultimo_ataque = now

    def _seguir_jogador(self, player_pos):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
        self.vx = dx * self.velocidade
        self.vy = dy * self.velocidade

    def _ataque_fogo_lateral(self, player_pos):
        # 3 direções: frente, esquerda, direita
        centro = self.get_hitbox().center
        for ang in [0, math.pi / 2, -math.pi / 2]:
            self._criar_projetil(centro, ang, 0.4, 1000)

    def _ataque_grito(self):
        if self.player:
            self.player.travado = True
            self.player.velocidade_original_grito = self.player.velocidadeMov
            self.player.velocidadeMov = 0.2
            time.set_timer(USEREVENT + 11, 1000)  # destrava
            time.set_timer(USEREVENT + 12, 5000)  # tira lentidão

    def _atacar_bolas_teleguiadas(self):
        if not self.player:
            return
        cx, cy = self.get_hitbox().center
        px, py = self.player.get_hitbox().center
        ang = math.atan2(py - cy, px - cx)
        self._criar_projetil((cx, cy), ang, 0.5, 2000)

    def _criar_projetil(self, origem, angulo, velocidade, duracao):
        x, y = origem
        vx = math.cos(angulo) * velocidade
        vy = math.sin(angulo) * velocidade
        self.player.projeteis.append({
            "x": x, "y": y,
            "vx": vx, "vy": vy,
            "dano": self.dano,
            "lifetime": duracao,
            "raio_hitbox": 16,
            "trail": [],
            "sprite": self.sprite_bola_fogo,
            "sprite_original": self.sprite_bola_fogo,
            "angulo": math.degrees(angulo) - 90
        })

    def desenhar(self, tela, playerpos, offset=(0, 0)):
        if not self.vivo:
            return
        frame = self.frames[self.frame_index]
        x_draw = self.x + offset[0]
        y_draw = self.y + offset[1]
        tela.blit(frame, (x_draw, y_draw))
        self.desenhar_outline_mouseover(tela, self.hp, self.hp_max)
        self.desenhar_dano(tela, offset)
        draw.rect(tela, (255, 0, 0), self.get_hitbox(), 1)

    def get_hitbox(self):
        return Rect(self.x + 20, self.y + 40, self.largura - 40, self.altura - 80)