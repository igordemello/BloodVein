from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font

class Hud:
    def __init__(self, player):
        self.player = player
        self.braco_fundo = image.load('assets/UI/HDEmptyHealthUI.png')
        self.braco_cima = image.load('assets/UI/HDFillHealthUI.png')
        self.fundo = image.load('assets/UI/tela_fundo1.jpeg')

    def desenhar(self, tela):
        tela.blit(self.fundo,(0,0))
        draw.rect(tela,(0,0,0),(0,0,1920,184))

        largura_total = self.braco_cima.get_width()
        altura_total = self.braco_cima.get_height()

        proporcao = max(0, min(1, self.player.hp / 100))

        largura_visivel = int(largura_total * proporcao)

        tela.blit(self.braco_fundo, (0, 30))

        if largura_visivel > 0:
            barra_cheia_cortada = self.braco_cima.subsurface((0, 0, largura_visivel, altura_total))
            tela.blit(barra_cheia_cortada, (0, 30))

