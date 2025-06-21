from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font
from player import Player



class Hud:
    def __init__(self, player):
        self.player = player
        self.bracoHp_fundo = transform.scale(image.load('assets/UI/HDEmptyHealthUI - Rotacionada.png').convert_alpha(), (192,576))
        self.bracoHp_cima = transform.scale(image.load('assets/UI/HDFillHealthUI - Rotacionada.png').convert_alpha(), (192,576))
        self.bracoSt_fundo = transform.flip(transform.scale(image.load('assets/UI/HDEmptyManaUI - Rotacionada.png').convert_alpha(), (192,576)), True , False)
        self.bracoSt_cima = transform.flip(transform.scale(image.load('assets/UI/HDFillManaUI - Rotacionada.png').convert_alpha(), (192,576)), True, False)

        self.almaIcon = transform.scale(image.load('assets/Itens/alma.png').convert_alpha(), (96,96))

        self.hud = image.load('assets/UI/Hud.png')
        self.fundo = image.load('assets/UI/tela_fundo1.png')
        self.fundo = transform.scale(self.fundo, (1920,1080))

    def desenhar(self, tela):
        almas_font = font.SysFont("Arial", 48)
        almas = almas_font.render(f"{self.player.almas}x", True, (255, 255, 255))
        almas_rect = almas.get_rect()
        almas_rect.right = 1690  # ponto fixo da direita (ajuste como preferir)
        almas_rect.top = 70

        tela.blit(self.fundo,(0,0))
        tela.blit(self.hud,(0,0))
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

        #desenhar itens:
        for i, (item, qtd) in enumerate(self.player.itens.items()):
            x = 200 + (i % 6) * 75  # 6 itens por linha
            y = 25 + (i // 6) * 64

            sprite = transform.scale(item.sprite, (64, 64))
            tela.blit(sprite, (x, y))

        #Desenha usos dos Itens ativos:
        if self.player.itemAtivo is not None:
            for x in range(0,self.player.itemAtivo.usos):
                draw.rect(tela, (0,255,0), (50+(x*25),144,20,8))

            sprite = transform.scale(self.player.itemAtivo.sprite, (96, 96))
            tela.blit(sprite, (60, 40))


        #Desenha número de almas
        #draw.rect(tela, (173,216,250), (1700, 75, 50,50))
        tela.blit(self.almaIcon, (1700, 40))
        tela.blit(almas, almas_rect)

        #STAMINA/MANA:
        braco_stamina = self.bracoSt_fundo
        larguraSt_total = (self.bracoSt_cima.get_width())
        alturaSt_total = self.bracoSt_cima.get_height() - 70

        proporcaoSt = max(0, min(1, self.player.st / 100))

        altura_visivelSt = int(alturaSt_total * proporcaoSt)


        tela.blit(braco_stamina, (1715, 510))

        if altura_visivelSt > 0:
            y_corte = self.bracoSt_cima.get_height() - altura_visivelSt

            barra_cheia_cortada = self.bracoSt_cima.subsurface((0, y_corte, larguraSt_total, altura_visivelSt)).copy()
            tela.blit(barra_cheia_cortada, (1715, 510 + y_corte))
