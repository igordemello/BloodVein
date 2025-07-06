from pygame import *
from pygame.math import Vector2
from efeito import *
from itensDic import ConjuntoItens
from random import sample
from botao import Botao


class Pause:
    def __init__(self):
        self.font = font.Font('assets/Fontes/alagard.ttf', 24)
        self.fontDesc = font.Font('assets/Fontes/alagard.ttf', 24)

        self.image_fundo = Surface((375, 500), SRCALPHA)
        self.image_fundo.fill((0, 0, 0, 0))


        self.botaocontinuar = Botao(image=None, pos=(1920//2, 400), text_input="CONTINUAR",
                               font=font.Font('assets/Fontes/alagard.ttf', 48), base_color=(228, 133, 40),
                               hovering_color=(100, 100, 100))
        self.botaoopcoes = Botao(image=None, pos=(1920 // 2, 500), text_input="OPÇÕES",
                               font=font.Font('assets/Fontes/alagard.ttf', 48), base_color=(228, 133, 40),
                               hovering_color=(100, 100, 100))

        self.botaosalvar = Botao(image=None, pos=(1920 // 2, 600), text_input="SALVAR",
                               font=font.Font('assets/Fontes/alagard.ttf', 48), base_color=(228, 133, 40),
                               hovering_color=(100, 100, 100))

        self.botaosair = Botao(image=None, pos=(1920 // 2, 700), text_input="SAIR",
                               font=font.Font('assets/Fontes/alagard.ttf', 48), base_color=(228, 133, 40),
                               hovering_color=(100, 100, 100))

        self.botoes = [self.botaocontinuar,self.botaoopcoes,self.botaosalvar,self.botaosair]
        self.escala = 3

        self.menu_ativo = False


    def pauseFuncionamento(self, tela):
        self.menu_ativo = True
        overlay = Surface(tela.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        pause_font = font.Font("assets/Fontes/alagard.ttf", 72)
        pause_text = pause_font.render("PAUSADO", True, (228, 133, 40))
        text_rect = pause_text.get_rect(center=(1920 // 2, 150))
        tela.blit(pause_text, text_rect)


        mouse_pos = mouse.get_pos()

        for botao in self.botoes:
            botao.changeColor(mouse_pos)
            botao.update(tela)

    def checar_clique_pause(self, mouse_pos):
        if not self.menu_ativo:
            return None
        if self.botaocontinuar.checkForInput(mouse_pos):
            self.menu_ativo = False
            return "continuar"
        if self.botaoopcoes.checkForInput(mouse_pos):
            return "opcoes" #ajeitar aq
        if self.botaosalvar.checkForInput(mouse_pos):
            return "salvar"
        if self.botaosair.checkForInput(mouse_pos):
            return "sair"
        return None
