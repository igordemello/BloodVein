from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import uniform, randint
from inimigo import Inimigo

class MorcegoSuicida(Inimigo):
    def __init__(self, x, y, largura=84, altura=84, hp=150, velocidade=2, dano=40):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        
        # Carrega spritesheets
        self.spritesheet_frente = image.load('./assets/Enemies/ExplodingBat_IdleSheet.png').convert_alpha()
        self.spritesheet_explosao = image.load('./assets/Enemies/ExplodingBat-AtteckSheet.png').convert_alpha()
        
        # Configurações de animação
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 8
        self.total_frames_explosao = 9
        
        # Inicializa frames
        self.frames_idle = [self.get_frame(self.spritesheet_frente, i) for i in range(self.total_frames)]
        self.frames_explosao = [self.get_frame(self.spritesheet_explosao, i) for i in range(self.total_frames_explosao)]
        self.frames = self.frames_idle  
        
        # Estado do morcego
        self.explodindo = False
        self.preparando_explosao = False
        self.tempo_explosao = 0
        self.duracao_explosao = 800  # ms
        self.tempo_preparacao = 200  # ms para piscar antes de explodir
        
        self.tipo_colisao = 'voador'


        
        # Visual
        self.alpha = 255
        self.piscando = False
        self.cor_piscar = (255, 150, 150)  # Vermelho claro para indicar perigo

    def get_frame(self, spritesheet, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def atualizar_animacao(self):
        if len(self.frames) == 0:  # Proteção contra lista vazia
            return
            
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def atualizar(self, player_pos, tela):
        if self.esta_atordoado():
            return

        if hasattr(self, 'stun_ativo') and self.stun_ativo:
            self.stun_ativo = False
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
        
        # Estado de explosão
        if self.explodindo:
            self.frames = self.frames_explosao  # Muda para frames de explosão
            self.atualizar_animacao()
            if now - self.tempo_explosao > self.duracao_explosao:
                self.hp = -1
                self.vivo = False
                self.alma_coletada = False
                self.vx = 0
                self.vy = 0
                self.rect.topleft = (self.x, self.y)
            return
        
        player_x = player_pos[0]
        player_y = player_pos[1]
        player_hitbox = Rect(player_x, player_y, 64, 64)

        # Pré-explosão (piscando)
        if self.preparando_explosao:
            self.frames = self.frames_idle  # Volta para frames normais (mas piscando)
            if now - self.tempo_explosao > self.tempo_preparacao:
                self.explodir(player_hitbox)
            else:
                # Efeito de piscar
                self.alpha = 150 if (now // 100) % 2 == 0 else 255
            return
            
        

        self.vx = 0
        self.vy = 0
        
        if abs(player_x - self.x) > 50:
            self.vx = self.velocidade if player_x > self.x else -self.velocidade
        if abs(player_y - self.y) > 50:
            self.vy = self.velocidade if player_y > self.y else -self.velocidade
            
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        

        
        if self.rect.colliderect(player_hitbox) and not self.preparando_explosao:
            self.preparar_explosao()
            
        self.atualizar_animacao()

    def preparar_explosao(self,):
        if not self.preparando_explosao:
            self.preparando_explosao = True
            self.tempo_explosao = time.get_ticks()
            self.frame_index = 0
            self.frame_time = 0
            self.velocidade_atual = 0

    def explodir(self,player_hitbox):
        self.explodindo = True
        self.tempo_explosao = time.get_ticks()
        self.frame_index = 0
        self.frame_time = 0

        if self.rect.colliderect(player_hitbox):
            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                self.dar_dano()

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo:
            return
            
        offset_x, offset_y = offset
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y



        vida_maxima = getattr(self, "hp_max", 100)
        largura_barra = 100
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = porcentagem * largura_barra
        
        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 2500:
            # Aplica offset na barra de vida
            draw.rect(tela, (255, 200, 200), (draw_x - 20, draw_y + 70, largura_barra, 5))
            draw.rect(tela, (255, 0, 0), (draw_x - 20, draw_y + 70, largura_hp, 5))
            draw.rect(tela, (255, 255, 255), (draw_x - 20, draw_y + 70, largura_barra, 5), 1)
        
        if len(self.frames) == 0:  # Proteção adicional
            return

        if self.explodindo:
            frame = self.frames_explosao[self.frame_index]
        else:
            frame = self.frames_idle[self.frame_index]

            
            
        # Aplica efeito visual se estiver prestes a explodir
        if self.preparando_explosao:
            temp_surface = frame.copy()
            if (time.get_ticks() // 100) % 2 == 0:
                temp_surface.fill(self.cor_piscar, special_flags=BLEND_MULT)
            temp_surface.set_alpha(self.alpha)
            tela.blit(temp_surface, (draw_x, draw_y))
        else:
            tela.blit(frame, (draw_x, draw_y))