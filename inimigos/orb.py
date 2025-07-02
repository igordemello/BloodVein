from pygame import *
import sys
from pygame.locals import QUIT
import math
from inimigo import Inimigo
class Orb(Inimigo):
    def __init__(self, x, y, largura, altura, nome="Orb",hp=100,velocidade=2,dano=10):
        super().__init__(x, y, largura, altura, hp,velocidade,dano)
        self.spritesheet = image.load('./assets/Enemies/EyeOrbSprite.png').convert_alpha()
        self.nome = nome
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 16
        self.usar_indices = list(range(0, self.total_frames, 2))
        self.carregar_sprites()