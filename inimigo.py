from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import randint


class Inimigo:
    def __init__(self,x,y,largura,altura,hp,velocidade=2):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.velocidade = velocidade

        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_time = 0
        self.knockback_duration = 200

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)
        self.hitboxArma = (70,100)

        self.old_x = x
        self.old_y = y

        self.hp = hp
        self.multDanoRecebido = 1 #isso multiplica o dano que o jogador causa, serve pra fazer bleed e pro parry
        self.vivo = True

        self.spritesheet = None
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 1
        self.usar_indices = [0]
        self.frames = []
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.10


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


    def atualizar(self, player_pos,tela):

        now = time.get_ticks()
        if now - self.knockback_time < self.knockback_duration:
            self.x += self.knockback_x
            self.y += self.knockback_y
            return
        self.old_x = self.x
        self.old_y = self.y
        #inimigo morrendo
        if self.hp <= 0:
            self.vivo = False
            return

        player_x = player_pos[0]
        player_y = player_pos[1]

        #colocar um range máximo que ele precisa ficar do jogador
        if abs(player_x - self.x) > 10:
            self.x += self.velocidade if player_x > self.x else -self.velocidade
        if abs(player_y - self.y) > 10:
            self.y += self.velocidade if player_y > self.y else -self.velocidade

        self.atualizar_animacao()




        



    def desenhar(self, tela, player_pos):

        if not self.frames:
            corpo = Rect(self.x, self.y, self.largura, self.altura) #substituir por sprite futuramente
            draw.rect(tela, (255,0,0), corpo)
        else:
            frame = self.frames[self.frame_index]
            tela.blit(frame, (self.x, self.y))

        #desenho da vida do inimigo
        draw.rect(tela, (255, 200, 200), (self.x - 20, self.y + 70, 100, 10))
        draw.rect(tela, (255, 0, 0), (self.x - 20, self.y + 70, self.hp, 10))


        rot_rect, rot_surf = self.get_hitbox_ataque(player_pos)
        tela.blit(rot_surf, rot_rect)

        
        

    def get_hitbox_ataque(self, player_pos):
        if not hasattr(self, '_last_angle') or self._last_pos != player_pos:
            player_x, player_y = player_pos
            dx = (player_x+32) - (self.x+32)
            dy = (player_y+32) - (self.y+32)
            self._last_angle = math.atan2(dy,dx)
            self._last_pos = player_pos
    

        #player_x = player_pos[0]
        #player_y = player_pos[1]

        #inimigo orbital
        #dx = (player_x+32) - (self.x+32)
        #dy = (player_y+32) - (self.y+32)
        
        angulo = self._last_angle

        orb_x = self.x + 32 + math.cos(angulo) * (self.radius+15)
        orb_y = self.y + 32 + math.sin(angulo) * (self.radius+15)

        Orb_rect = Rect(0,0,*(self.orbital_size))
        Orb_rect.center = (orb_x, orb_y)

        #esse daqui é a hitbox do ataque do inimigo
        orb_surf = Surface(self.hitboxArma, SRCALPHA)
        draw.rect(orb_surf, (255,0,0), orb_surf.get_rect(), width=1 ) #quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_surf = transform.rotate(orb_surf, -math.degrees(angulo)) #quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_rect = rot_surf.get_rect(center=Orb_rect.center) #quadrado sem preenchimento vermelho   que fica com o inimigo

        #tela.blit(rot_surf, Rot_rect) #quadrado sem preenchimento vermelho   que fica com o inimigo

        return rot_rect, rot_surf


    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)
    
    def voltar_posicao(self):
        self.x = self.old_x
        self.y = self.old_y

    