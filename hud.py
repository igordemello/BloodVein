from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font

class Hud:
    def __init__(self, player):
        self.player = player

    def desenhar(self, tela):
        draw.rect(tela, (0,0,0), (0,0, 1920, 184))

        vida_largura = 100 * (self.player.hp / 20)

        draw.rect(tela, (255, 0, 0), (32, 32, vida_largura, 50))


