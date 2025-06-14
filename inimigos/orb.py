from pygame import *
import sys
from pygame.locals import QUIT
import math
from inimigo import Inimigo

class Orb(Inimigo):
    def __init__(self, x, y, largura, altura, hp=100,velocidade=2):
        super().__init__(x, y, largura, altura, hp,velocidade)
        self.spritesheet = image.load('./assets/Enemies/EyeOrbSprite.png')

        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 16
        self.usar_indices = list(range(0, self.total_frames, 2))

        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.10

        self.frames = [self.get_frame(i) for i in self.usar_indices]

    def get_frame(self, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(self.spritesheet, (0, 0), rect)

        frame = transform.scale(frame, (self.largura,self.altura))
        return frame

    def desenhaOrb(self, tela, player_pos):
        if self.hp <= 0:
            self.vivo = False
            return
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        frame = self.frames[self.frame_index]
        tela.blit(frame, (self.x, self.y))

        draw.rect(tela, (255, 200, 200), (self.x - 20, self.y + 70, 100, 10))
        draw.rect(tela, (255, 0, 0), (self.x-20, self.y+70, self.hp, 10))

        rot_rect, rot_surf = self.get_hitbox_ataque(player_pos)
        tela.blit(rot_surf, rot_rect)
