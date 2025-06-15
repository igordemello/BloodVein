from pygame import *
import sys
from pygame.locals import QUIT
import math


class Inimigo:
    def __init__(self,x,y,largura,altura,hp,velocidade=2):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.velocidade = velocidade

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)
        self.hitboxArma = (70,100)

        self.old_x = x
        self.old_y = y

        self.hp = hp
        self.vivo = True

    def atualizar(self, player_pos):
        self.old_x = self.x
        self.old_y = self.y

        if self.hp <= 0:
            self.vivo = False
            return

        player_x = player_pos[0]
        player_y = player_pos[1]

        #colocar um range máximo que ele precisa ficar do jogador
        if player_x not in range(self.x, self.x+25):
            if player_x > self.x+100:
                self.x += self.velocidade
            elif player_x < self.x:
                self.x -= self.velocidade
        if player_y not in range(self.y, self.y+25):
            if player_y > self.y+100:
                self.y += self.velocidade
            elif player_y < self.y:
                self.y -= self.velocidade


        



    def desenhar(self, tela, player_pos):

        corpo = Rect(self.x, self.y, self.largura, self.altura) #substituir por sprite futuramente
        draw.rect(tela, (255,0,0), corpo)


        rot_rect, rot_surf = self.get_hitbox_ataque(player_pos)
        tela.blit(rot_surf, rot_rect)

        
        

    def get_hitbox_ataque(self, player_pos):
        player_x = player_pos[0]
        player_y = player_pos[1]

        #inimigo orbital
        dx = (player_x+32) - (self.x+32)
        dy = (player_y+32) - (self.y+32)
        angulo = math.atan2(dy,dx)

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

    