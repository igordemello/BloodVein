from pygame import *
from pygame.locals import QUIT
import sys
from botao import Botao
from pygame.math import Vector2
import cv2
import numpy as np


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
            Botao(None, (600, 420), "Iniciar", self.fonte_botoes, self.cor_base, self.cor_hover, "jogo"),
            Botao(None, (600, 520), "Continuar", self.fonte_botoes, self.cor_base, self.cor_hover, "continuar"),
            Botao(None, (600, 620), "Opções", self.fonte_botoes, self.cor_base, self.cor_hover, "opcoes"),
            Botao(None, (600, 720), "Conquistas", self.fonte_botoes, self.cor_base, self.cor_hover, "pontuacao"),
            Botao(None, (600, 820), "Sair", self.fonte_botoes, self.cor_base, self.cor_hover, "sair"),
        ]

        self.hover_escala = [Vector2(1.0, 0.0) for _ in self.botoes]

        #vídeo
        self.intro_video = cv2.VideoCapture("assets/UI/inicio.mp4")
        self.loop_video = cv2.VideoCapture("assets/UI/loop.mp4")
        self.showing_intro = True
        self.menu_active = False

        self.index_selecionado = 0
        self.espada_img = image.load("assets/UI/Espada menu.png").convert_alpha()
        self.espada_img = transform.scale(self.espada_img, (50, 50))

    def cv2_to_pygame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")
    

    def run(self):  

        if self.showing_intro:
            ret, frame = self.intro_video.read()
            if ret and frame is not None:
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                pygame_frame = self.cv2_to_pygame(frame)
                self.screen.blit(pygame_frame, (0, 0))
            else:
                self.showing_intro = False
                self.intro_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            ret, frame = self.loop_video.read()
            if not ret or frame is None:
                self.loop_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.loop_video.read()

            if ret and frame is not None:
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                pygame_frame = self.cv2_to_pygame(frame)
                self.screen.blit(pygame_frame, (0, 0))


    def desenho(self, tela):
        titulo_sombra = self.fonte.render("Blood Vein", True, (30, 30, 30))
        tela.blit(titulo_sombra, (200 + 4, 100 + 4))

        titulo = self.fonte.render("Blood Vein", True, (253, 246, 225))
        tela.blit(titulo, (200, 100))

        mouse_pos = mouse.get_pos()
        for i, botao in enumerate(self.botoes):
            is_hovered = botao.rect.collidepoint(mouse_pos) or i == self.index_selecionado

            if is_hovered:
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
