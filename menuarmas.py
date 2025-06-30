from pygame import *
from pygame.math import Vector2
from efeito import *
from itensDic import ConjuntoItens
from random import sample
from botao import Botao
from armas import *


class MenuArmas:
    def __init__(self):
        self.lista_mods = ListaMods()
        self.armasDisp = [
            LaminaDaNoite("comum", self.lista_mods),
            Chigatana("comum", self.lista_mods),
            Karambit("comum", self.lista_mods),
            EspadaDoTita("comum", self.lista_mods),
            MachadoDoInverno("comum", self.lista_mods),
            EspadaEstelar("comum", self.lista_mods),
            MarteloSolar("comum", self.lista_mods),
            Arco("comum", self.lista_mods)
        ]

        self.pos = 0
        self.arma_sorteada = self.armasDisp[self.pos]
        self.font = font.Font('assets/Fontes/alagard.ttf', 18)
        self.fontDesc = font.Font('assets/Fontes/alagard.ttf', 18)

        self.estado_hover = Vector2(1.0, 0.0)

        self.image_fundo = Surface((375, 500), SRCALPHA)
        self.image_fundo.fill((0, 0, 0, 0))

        screen_width, screen_height = display.get_surface().get_size()
        self.botao = Botao(
            image=self.image_fundo,
            pos=(screen_width // 2, screen_height // 2),
            text_input="",
            font=self.font,
            base_color=(255, 255, 255),
            hovering_color=(0, 0, 0)
        )

        self.botaosair = Botao(image=None, pos=(200, 980), text_input="Sair",
                               font=font.Font('assets/Fontes/alagard.ttf', 32),
                               base_color=(244, 26, 43), hovering_color=(202, 56, 68))

        self.menu_ativo = False
        self.arma_escolhida = None

    def menuEscolherItens(self, tela):
        overlay = Surface(tela.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        mouse_pos = mouse.get_pos()

        carta_width, carta_height = 375, 500
        carta_rect = Rect(0, 0, carta_width, carta_height)
        carta_rect.center = (tela.get_width() // 2, tela.get_height() // 2)


        is_hovered = carta_rect.collidepoint(mouse_pos)
        alvo = Vector2(1.1, -30) if is_hovered else Vector2(1.0, 0.0)
        self.estado_hover = self.estado_hover.lerp(alvo, 0.1)

        scale = self.estado_hover.x
        deslocamento_y = self.estado_hover.y

        width = int(carta_width * scale)
        height = int(carta_height * scale)
        pos_x = tela.get_width() // 2 - width // 2
        pos_y = tela.get_height() // 2 - height // 2 + deslocamento_y

        sprite_raridade = image.load(f"assets/itens/carta_{self.arma_sorteada.raridade}.png").convert_alpha()
        sprite_carta = transform.scale(sprite_raridade, (width, height))
        tela.blit(sprite_carta, (pos_x, pos_y))

        spriteIcon = image.load(self.arma_sorteada.spriteIcon).convert_alpha()
        sprite_arma = transform.scale(spriteIcon, (int(128 * scale), int(128 * scale)))
        arma_center_x = pos_x + width // 2 - sprite_arma.get_width() // 2
        tela.blit(sprite_arma, (arma_center_x, pos_y + int(40 * scale)))

        titulo = self.font.render(self.arma_sorteada.nome, True, (0, 0, 0))
        titulo_rect = titulo.get_rect(center=(pos_x + width // 2, pos_y + 20 + int(height * 0.42)))
        tela.blit(titulo, titulo_rect)


    def checar_clique_menu(self, mouse_pos):

        carta_rect = Rect(0, 0, 375, 500)
        carta_rect.center = (display.get_surface().get_width() // 2,
                             display.get_surface().get_height() // 2)

        if carta_rect.collidepoint(mouse_pos):
            self.arma_sorteada.aplicaModificador()  # Aplica os modificadores
            print(f"Arma escolhida: {self.arma_sorteada.nome}")
            self.menu_ativo = False
            return self.arma_sorteada

        else:
            return None

    def scrollMenu(self, input):
        if input == ">":
            if self.pos == len(self.armasDisp)-1:
                self.pos = 0
            else:
                self.pos += 1
        else:
            if self.pos == 0:
                self.pos = len(self.armasDisp)-1
            else:
                self.pos -= 1

        self.arma_sorteada = self.armasDisp[self.pos]