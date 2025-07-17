from pygame import *
import math
from pygame import time
from inimigo import Inimigo
from pathfinding import a_star

def pixel_para_grid(x, y, offset, tile_size_scaled):
    grid_x = int((x - offset[0]) / tile_size_scaled)
    grid_y = int((y - offset[1]) / tile_size_scaled)
    return grid_x, grid_y

def grid_para_pixel(grid_x, grid_y, offset, tile_size_scaled):
    x = offset[0] + (grid_x * tile_size_scaled) + (tile_size_scaled / 2)
    y = offset[1] + (grid_y * tile_size_scaled) + (tile_size_scaled / 2)
    return x, y

class MorcegoPadrao(Inimigo):
    def __init__(self, x, y, largura=64, altura=64, hp=80, velocidade=2, dano=15):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.sprites_idle = image.load('./assets/Enemies/morcego_idle.png').convert_alpha()
        self.sprites_voando = image.load('./assets/Enemies/morcego_correr.png').convert_alpha()

        self.frame_width = 27
        self.frame_height = 36
        self.animation_speed = 0.12

        self.frames_idle = [self.get_frame(self.sprites_idle, i) for i in range(4)]
        self.frames_voando = [self.get_frame(self.sprites_voando, i) for i in range(6)]
        self.frames = self.frames_idle
        self.estado = 'idle'

        self.raio_ataque = 50
        self.atacando = False
        self.tempo_ataque = 0
        self.duracao_ataque = 400

        self.tipo_colisao = 'obstaculo'
        self.ultimo_objetivo = None
        self.caminho_atual = []
        self.tile_size_scaled = 32 * 3.25
        self.vivo = True

    def get_frame(self, spritesheet, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def atualizar(self, player_pos, tela, matriz_colisao, offset_mapa):
        if self.esta_atordoado() or self.hp <= 0:
            self.vivo = False
            self.vx = 0
            self.vy = 0
            return
        
        
        # Verificar knockback primeiro
        now = time.get_ticks()
        if now - self.knockback_time < self.knockback_duration:
            # Aplicar knockback (se houver) e retornar
            self.x += self.vx
            self.y += self.vy
            return
        
        #PATHFINDING A*
        # 1. Obter offset e tamanho do tile (IGUAL AO MAPA)
        tile_size_scaled = self.tile_size_scaled
        
        # 2. Converter posições para grid
        start = pixel_para_grid(self.x, self.y, offset_mapa, tile_size_scaled)
        goal = pixel_para_grid(player_pos[0], player_pos[1], offset_mapa, tile_size_scaled)
        
        # 3. Validar coordenadas
        if not (0 <= start[1] < len(matriz_colisao)) or not (0 <= start[0] < len(matriz_colisao[0])):
            return
            
        if not (0 <= goal[1] < len(matriz_colisao)) or not (0 <= goal[0] < len(matriz_colisao[0])):
            return
            
        # 4. Verificar se precisa recalcular caminho
        if self.ultimo_objetivo != goal or not self.caminho_atual:
            self.caminho_atual = a_star(matriz_colisao, start, goal)
            self.ultimo_objetivo = goal

        # 5. Seguir caminho
        if self.caminho_atual and len(self.caminho_atual) > 1:
            proximo = self.caminho_atual[1]
            
            # Converter para posição mundial (centro do tile)
            destino_x, destino_y = grid_para_pixel(
                proximo[0], proximo[1], 
                offset_mapa, 
                tile_size_scaled
            )
            
            # Calcular direção
            dx = destino_x - self.x
            dy = destino_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist > 5:  # Só move se estiver longe
                self.vx = (dx / dist) * self.velocidade
                self.vy = (dy / dist) * self.velocidade
            else:
                self.caminho_atual.pop(0)  # Chegou neste nó
        
        # Aplicar movimento
        self.x += self.vx
        self.y += self.vy

        # Resetar velocidade para evitar movimento contínuo
        self.vx = self.vy = 0
        #ATÉ AQUI O PATHFINDING

        if self.atacando:
            if now - self.tempo_ataque > self.duracao_ataque:
                self.atacando = False

        self.estado = 'voando'
        self.frames = self.frames_voando
        self.rect.topleft = (round(self.x), round(self.y))

        if not self.atacando:
            player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
            if self.rect.colliderect(player_rect.inflate(self.raio_ataque, self.raio_ataque)):
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
        self.desenhar_outline_mouseover(tela)

        offset_x, offset_y = offset
        draw_x = round(self.x) + offset_x
        draw_y = round(self.y) + offset_y
        tela.blit(self.frames[self.frame_index], (draw_x, draw_y))

        vida_maxima = getattr(self, "hp_max", 100)
        largura_barra = 100
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = porcentagem * largura_barra

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 2500:
            draw.rect(tela, (255, 200, 200), (draw_x - 20, draw_y + 70, largura_barra, 5))
            draw.rect(tela, (255, 0, 0), (draw_x - 20, draw_y + 70, largura_hp, 5))
            draw.rect(tela, (255, 255, 255), (draw_x - 20, draw_y + 70, largura_barra, 5), 1)
