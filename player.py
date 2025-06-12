from pygame import *
import sys
from pygame.locals import QUIT
import math

class Player():
    def __init__(self, x, y, largura, altura, hp=100, velocidade=0.3):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

        self.hp = hp
        self.velocidade = velocidade
        self.rate = 1

        self.old_x = x
        self.old_y = y

        self.radius = 70
        self.orbital_size = (40, 20)
        self.hitbox_arma = (70, 100)

        self.atacou = False

        #controles para o dash
        self.dash_cooldown = 0  
        self.dash_duration = 0  
        self.dash_cooldown_max = 1000 
        self.dash_duration_max = 150  
        self.is_dashing = False 
        self.last_dash_time = 0 

    def _dash(self, dt, teclas, direcao):
        current_time = time.get_ticks()

        if (current_time - self.last_dash_time > self.dash_cooldown_max and 
            not self.is_dashing and teclas[K_SPACE]):
            
            self.last_dash_time = current_time
            self.is_dashing = True
            self.dash_duration = 0

        if self.is_dashing:
            oldv = self.velocidade
            self.velocidade = 0.7
            if direcao == 'd': self.x += self.velocidade * dt
            elif direcao == 'a': self.x -= self.velocidade * dt
            elif direcao == 'w': self.y -= self.velocidade * dt
            elif direcao == 's': self.y += self.velocidade * dt
            self.velocidade = oldv
            

            self.dash_duration += dt
            if self.dash_duration >= self.dash_duration_max:
                self.is_dashing = False


    def atualizar(self, dt, teclas):
        self.old_x = self.x
        self.old_y = self.y

        if teclas[K_d]:
            self.x += self.velocidade * dt
            self._dash(dt, teclas, 'd')
        if teclas[K_a]:
            self.x -= self.velocidade * dt
            self._dash(dt, teclas, 'a')
        if teclas[K_w]:
            self.y -= self.velocidade * dt
            self._dash(dt, teclas, 'w')
        if teclas[K_s]:
            self.y += self.velocidade * dt
            self._dash(dt, teclas, 's')

        self.hp -= 0.05 * self.rate

    def calcular_angulo(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        dx = mouse_x - (self.x + 32)
        dy = mouse_y - (self.y + 32)
        return math.atan2(dy, dx)

    def get_rotated_rect_ataque(self, mouse_pos):
        angle = self.calcular_angulo(mouse_pos)

        orbital2_x = self.x + 32 + math.cos(angle) * (self.radius + 15)
        orbital2_y = self.y + 32 + math.sin(angle) * (self.radius + 15)

        orbital_rect2 = Rect(0, 0, *self.orbital_size)
        orbital_rect2.center = (orbital2_x, orbital2_y)

        orbital_surf2 = Surface(self.hitbox_arma, SRCALPHA)
        draw.rect(orbital_surf2, (255, 0, 0), orbital_surf2.get_rect(), width=1)
        rotated_surf2 = transform.rotate(orbital_surf2, -math.degrees(angle))
        rotated_rect2 = rotated_surf2.get_rect(center=orbital_rect2.center)

        return rotated_surf2, rotated_rect2

    def desenhar(self, tela, mouse_pos):
        corpo = Rect(self.x, self.y, self.largura, self.altura)
        draw.rect(tela, (0, 255, 0), corpo)

        angle = self.calcular_angulo(mouse_pos)

        orbital_x = self.x + 32 + math.cos(angle) * self.radius
        orbital_y = self.y + 32 + math.sin(angle) * self.radius

        orbital_rect = Rect(0, 0, *self.orbital_size)
        orbital_rect.center = (orbital_x, orbital_y)

        orbital_surf = Surface(self.orbital_size, SRCALPHA)
        orbital_surf.fill((0, 0, 255))
        rotated_surf = transform.rotate(orbital_surf, -math.degrees(angle))
        rotated_rect = rotated_surf.get_rect(center=orbital_rect.center)

        tela.blit(rotated_surf, rotated_rect)

        # Hitbox do ataque
        rotated_surf2, rotated_rect2 = self.get_rotated_rect_ataque(mouse_pos)
        tela.blit(rotated_surf2, rotated_rect2)

    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)

    def voltar_posicao(self):
        self.x = self.old_x
        self.y = self.old_y
