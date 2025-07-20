from pygame import *
import math
from inimigo import Inimigo
from utils import resource_path
from pathfinding import a_star

def pixel_para_grid(x, y, offset, tile_size_scaled):
    grid_x = int((x - offset[0]) / tile_size_scaled)
    grid_y = int((y - offset[1]) / tile_size_scaled)
    return grid_x, grid_y

def grid_para_pixel(grid_x, grid_y, offset, tile_size_scaled):
    x = offset[0] + (grid_x * tile_size_scaled)
    y = offset[1] + (grid_y * tile_size_scaled)
    return x, y

class Zombie(Inimigo):
    def __init__(self, x, y, largura, altura, nome="Zombie", hp=150, velocidade=2.2, dano=15):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.nome = nome

        # Atributos de pathfinding
        self.ultimo_objetivo = None
        self.caminho_atual = []
        self.tile_size_scaled = 32 * 3.25

        # Sprites
        self.sprites_andando_frente = image.load(resource_path('./assets/Enemies/Zombie_andando.png')).convert_alpha()
        self.sprites_andando_costas = image.load(resource_path('./assets/Enemies/Zombie_andando_costas.png')).convert_alpha()
        self.sprites_andando_lado = image.load(resource_path('./assets/Enemies/Zombie_andando_lado.png')).convert_alpha()
        self.sprites_ataque = image.load(resource_path('./assets/Enemies/Zombie_ataque.png')).convert_alpha()

        self.frame_width = 32
        self.frame_height = 32
        self.animation_speed = 0.15

        self.frames_frente = self.carregar_frames(self.sprites_andando_frente, 7)
        self.frames_costas = self.carregar_frames(self.sprites_andando_costas, 7)
        self.frames_lado = self.carregar_frames(self.sprites_andando_lado, 8)
        self.frames_ataque = self.carregar_frames(self.sprites_ataque, 5)

        self.frames = self.frames_frente

        self.estado = "perseguindo"
        self.direcao = "frente"

        # Ataque
        self.combo_etapa = 0
        self.max_combo = 3
        self.tempo_ultimo_ataque = 0
        self.intervalo_entre_socos = 500  # tempo entre os socos do combo
        self.cooldown_ataque = 2000  # tempo de espera após o combo
        self.em_cooldown = False
        self.tipo_colisao = 'obstaculo'

    def carregar_frames(self, spritesheet, num_frames):
        frames = []
        for i in range(num_frames):
            rect = Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
            frame.blit(spritesheet, (0, 0), rect)
            frame = transform.scale(frame, (self.largura, self.altura))
            frames.append(frame)
        return frames

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def atualizar(self, player_pos, tela, matriz_colisao, offset_mapa):
        now = time.get_ticks()

        if self.esta_atordoado() or self.hp <= 0:
            self.vivo = False
            self.vx = 0
            self.vy = 0
            return

        # Knockback
        if now - self.knockback_time < self.knockback_duration:
            self.x += self.vx
            self.y += self.vy
            return

        # PATHFINDING A*
        tile_size_scaled = self.tile_size_scaled
        center_x = self.x + self.largura // 2
        center_y = self.y + self.altura // 2

        start = pixel_para_grid(center_x, center_y, offset_mapa, tile_size_scaled)
        goal = pixel_para_grid(player_pos[0], player_pos[1], offset_mapa, tile_size_scaled)

        if not (0 <= start[1] < len(matriz_colisao)) or not (0 <= start[0] < len(matriz_colisao[0])):
            return
        if not (0 <= goal[1] < len(matriz_colisao)) or not (0 <= goal[0] < len(matriz_colisao[0])):
            return

        if self.ultimo_objetivo != goal or not self.caminho_atual:
            self.caminho_atual = a_star(matriz_colisao, start, goal)
            self.ultimo_objetivo = goal

        # Se estiver perto o suficiente do jogador, atacar
        distancia = math.hypot(player_pos[0] - center_x, player_pos[1] - center_y)
        if distancia < 150 and not self.em_cooldown:
            self.caminho_atual = []
            if now - self.tempo_ultimo_ataque > self.intervalo_entre_socos:
                self.estado = "atacando"
                self.frames = self.frames_ataque
                self.frame_index = 0
                self.tempo_ultimo_ataque = now
                self.combo_etapa += 1

                if hasattr(self, "dar_dano") and callable(self.dar_dano):
                    self.dar_dano()

                if self.combo_etapa >= self.max_combo:
                    self.combo_etapa = 0
                    self.em_cooldown = True
                    self.tempo_ultimo_ataque = now
            self.vx = self.vy = 0
        elif self.em_cooldown:
            if now - self.tempo_ultimo_ataque > self.cooldown_ataque:
                self.em_cooldown = False
        else:
            self.estado = "perseguindo"
            if self.caminho_atual and len(self.caminho_atual) > 1:
                proximo = self.caminho_atual[1]
                destino_x, destino_y = grid_para_pixel(proximo[0], proximo[1], offset_mapa, tile_size_scaled)
                dx = destino_x - self.x
                dy = destino_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 5:
                    self.vx = (dx / dist) * self.velocidade
                    self.vy = (dy / dist) * self.velocidade
                else:
                    self.caminho_atual.pop(0)

                # Direção para animação
                if abs(dx) > abs(dy):
                    self.direcao = "lado"
                    if self.frames != self.frames_lado:
                        self.frames = self.frames_lado
                        self.frame_index = 0

                    # Verifica se deve inverter a sprite
                    self.inverter_lado = dx < 0  # Se indo para a esquerda, inverte
                else:
                    self.direcao = "costas" if dy < 0 else "frente"
                    novo_frames = self.frames_costas if self.direcao == "costas" else self.frames_frente
                    if self.frames != novo_frames:
                        self.frames = novo_frames
                        self.frame_index = 0
                    self.inverter_lado = False  # Não inverter para frente/costas

                self.set_velocidade_x(self.vx)
                self.set_velocidade_y(self.vy)

        self.rect.topleft = (round(self.x), round(self.y))
        self.atualizar_animacao()

        if hasattr(self, 'veneno_ativo') and self.veneno_ativo:
            if now >= self.veneno_proximo_tick and self.veneno_ticks > 0:
                self.hp -= self.veneno_dano_por_tick
                self.veneno_ticks -= 1
                self.veneno_proximo_tick = now + self.veneno_intervalo

                # Inicia animação de hit como feedback visual (opcional)
                self.anima_hit = True
                self.time_last_hit_frame = now
                self.ultimo_dano = self.veneno_dano_por_tick
                self.ultimo_dano_tempo = time.get_ticks()

            if self.veneno_ticks <= 0:
                self.veneno_ativo = False

    def desenhar(self, tela, playerpos, offset=(0, 0)):
        if not self.vivo or not self.frames:
            return
        
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        offset_x, offset_y = offset
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y

        self.desenhar_outline_mouseover(tela, self.hp, self.hp_max)

        frame = self.frames[self.frame_index]

        # Aplica efeito de hit, se necessário
        if self.anima_hit:
            frame = self.aplicar_efeito_hit(frame)

        # Aplica flip horizontal se necessário
        if self.direcao == "lado" and self.inverter_lado:
            frame = transform.flip(frame, True, False)

        tela.blit(frame, (draw_x, draw_y))
        self.desenhar_dano(tela, offset)

    def get_hitbox(self):
        return Rect(self.x+20, self.y+20, self.largura-40, self.altura-40)