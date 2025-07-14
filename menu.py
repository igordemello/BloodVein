from pygame import *
from pygame.locals import QUIT
import sys
from botao import Botao
from pygame.math import Vector2
import cv2
import numpy as np
from som import GerenciadorDeSom
from som import som
from som import GerenciadorDeMusica
from som import musica


class gerenciamento():
    def __init__(self):
        self.modo = "menu"


class Menu():
    def __init__(self, SCREEN):
        self.screen = SCREEN
        self.screen_width, self.screen_height = self.screen.get_size()
        self.fonte = font.Font("assets/Fontes/Alkhemikal.ttf", 180)
        self.fonte_botoes = font.Font("assets/Fontes/alagard.ttf", 72)

        self.cor_base = (253, 246, 225)
        self.cor_hover = (0, 0, 0)

        self.botoes = [
            Botao(None, (600, 420), "Novo Jogo", self.fonte_botoes, self.cor_base, self.cor_hover, "jogo"),
            Botao(None, (600, 520), "Continuar", self.fonte_botoes, self.cor_base, self.cor_hover, "continuar"),
            Botao(None, (600, 620), "Opções", self.fonte_botoes, self.cor_base, self.cor_hover, "opcoes"),
            Botao(None, (600, 720), "Sair", self.fonte_botoes, self.cor_base, self.cor_hover, "sair"),
        ]

        self.hover_escala = [Vector2(1.0, 0.0) for _ in self.botoes]
        self.ultimo_hover = -1

    def desenho(self, tela):
        tela.blit(self.menu, (0,0))
        musica.tocar("BloodVein SCORE/OST/MainMenuTheme.mp3")
        titulo_sombra = self.fonte.render("Blood Vein", True, (30, 30, 30))
        tela.blit(titulo_sombra, (200 + 4, 100 + 4))

        titulo = self.fonte.render("Blood Vein", True, (253, 246, 225))
        tela.blit(titulo, (200, 100))

        mouse_pos = mouse.get_pos()
        for i, botao in enumerate(self.botoes):
            is_hovered = botao.rect.collidepoint(mouse_pos) or i == self.index_selecionado

            if is_hovered:
                if i != self.ultimo_hover:  
                    som.tocar("hover")  
                    self.ultimo_hover = i  

                self.index_selecionado = i

            alvo = Vector2(1.1, -5) if is_hovered else Vector2(1.0, 0.0)
            self.hover_escala[i] = self.hover_escala[i].lerp(alvo, 0.1)

            scale = self.hover_escala[i].x
            offset_y = self.hover_escala[i].y

            cor = botao.hovering_color if is_hovered else botao.base_color
            texto = botao.font.render(botao.text_input, True, cor)
            largura = int(texto.get_width() * scale)
            altura = int(texto.get_height() * scale)
            texto = transform.scale(texto, (largura, altura))

            sombra = botao.font.render(botao.text_input, True, (50, 50, 50))
            sombra = transform.scale(sombra, (largura, altura))

            pos_x = botao.x_pos - largura // 2
            pos_y = botao.y_pos - altura // 2 + int(offset_y)

            tela.blit(sombra, (pos_x + 3, pos_y + 3))
            tela.blit(texto, (pos_x, pos_y))

            if i == self.index_selecionado:
                espada_x = pos_x - self.espada_img.get_width() - 20
                espada_y = pos_y + (texto.get_height() // 2) - (self.espada_img.get_height() // 2)
                tela.blit(self.espada_img, (espada_x, espada_y))


    def checar_clique(self, pos):
        for botao in self.botoes:
            if botao.checkForInput(pos):
                return botao.value
        return None