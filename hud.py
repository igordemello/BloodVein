from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font

class Hud:
    def __init__(self, player):
        self.player = player
        self.bracoHp_fundo = transform.scale(image.load('assets/UI/HDEmptyHealthUI - Rotacionada.png'), (192,576))
        self.bracoHp_cima = transform.scale(image.load('assets/UI/HDFillHealthUI - Rotacionada.png'), (192,576))
        self.bracoSt_fundo = transform.scale(image.load('assets/UI/HDEmptyManaUI - Rotacionada.png'), (192,576))
        self.bracoSt_cima = transform.scale(image.load('assets/UI/HDFillManaUI - Rotacionada.png'), (192,576))
        self.fundo = image.load('assets/UI/tela_fundo1.jpeg')

    def desenhar(self, tela):
        tela.blit(self.fundo,(0,0))
        draw.rect(tela,(0,0,0),(0,0,1920,184))
        #HP:
        larguraHp_total = (self.bracoHp_cima.get_width())
        alturaHp_total = self.bracoHp_cima.get_height() - 100

        proporcaoHp = max(0, min(1, self.player.hp / 100))

        altura_visivelHp = int(alturaHp_total * proporcaoHp)

        tela.blit(self.bracoHp_fundo, (15, 510))


        if altura_visivelHp > 0:
            y_corte = self.bracoHp_cima.get_height() - altura_visivelHp

            barra_cheia_cortada = self.bracoHp_cima.subsurface((0, y_corte, larguraHp_total, altura_visivelHp)).copy()
            tela.blit(barra_cheia_cortada, (15, 510 + y_corte))

        #STAMINA/MANA:
        braco_stamina = self.bracoSt_fundo
        braco_stamina = transform.flip(braco_stamina, True, False)
        larguraSt_total = (self.bracoSt_cima.get_width())
        alturaSt_total = self.bracoSt_cima.get_height() - 70

        proporcaoSt = max(0, min(1, self.player.st / 100))

        altura_visivelSt = int(alturaSt_total * proporcaoSt)


        tela.blit(braco_stamina, (1715, 510))

        if altura_visivelSt > 0:
            y_corte = self.bracoSt_cima.get_height() - altura_visivelSt

            barra_cheia_cortada = self.bracoSt_cima.subsurface((0, y_corte, larguraSt_total, altura_visivelSt)).copy()
            barra_cheia_cortada = transform.flip(barra_cheia_cortada, True, False)
            tela.blit(barra_cheia_cortada, (1715, 510 + y_corte))
