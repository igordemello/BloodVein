from pygame import *
import sys
from pygame.locals import QUIT
import math
from bau import Bau
from hud import Hud
from inimigo import Inimigo
from player import Player
from botao import Botao
from mapa import Mapa
from colisao import Colisao
from inimigos.orb import Orb
from inimigos.MouthOrbBoss import MouthOrb
from sala import Sala
from itensDic import *
from gerenciador_andar import GerenciadorAndar
from menu import Menu
from menu import gerenciamento
from loja import Loja
from minimapa import Minimapa
from menuarmas import *
from screen_shake import screen_shaker
from save_manager import SaveManager
from som import GerenciadorDeSom
from som import som
from pause import Pause
import os
import shutil

class Inventario():
    def __init__(self, screen, player, hud):
        self.screen = screen
        self.visible = False
        self.player = player
        self.hud = hud
        self.fundo = image.load('assets/UI/inventario_fundo.png').convert_alpha()

        self.item_width, self.item_height = 230, 240
        
        self.carta_imgs = {
            "comum": transform.scale(image.load("assets/itens/carta_comum.png").convert_alpha(), (self.item_width + 40, self.item_height + 130)),
            "rara": transform.scale(image.load("assets/itens/carta_rara.png").convert_alpha(), (self.item_width + 40, self.item_height + 130)),
            "lendaria": transform.scale(image.load("assets/itens/carta_lendaria.png").convert_alpha(), (self.item_width + 40, self.item_height + 130)),
            "ativo": transform.scale(image.load("assets/itens/carta_ativo.png").convert_alpha(), (self.item_width + 40, self.item_height + 130))
        }

        self.fator_escala_arma = (self.item_width + 40) / 53

    def toggle(self):
        self.visible = not self.visible

    

    def desenhar(self):
        if not self.visible:
            return

        self.screen.blit(self.fundo, (0, 0))

        mouse_x, mouse_y = mouse.get_pos()

        item_hover = None
        item_hover_pos = (0, 0)

        #itens passivos
        for i, (item, qtd) in enumerate(self.player.itens.items()):
            x = 765 + (i % 3) * 150
            y = 425 + (i // 3) * 175
            sprite = transform.scale(item.sprite, (100, 100))
            self.screen.blit(sprite, (x, y))

            rect_item = Rect(x, y, 100, 100)
            if rect_item.collidepoint(mouse_x, mouse_y):
                item_hover = item
                item_hover_pos = (x, y)

        #item ativo
        if self.player.itemAtivo is not None:
            item_ativo = self.player.itemAtivo
            ativo_x, ativo_y = 910, 220
            sprite = transform.scale(item_ativo.sprite, (100, 100))
            self.screen.blit(sprite, (ativo_x, ativo_y))

            

            rect_ativo = Rect(ativo_x, ativo_y, 100, 100)
            if rect_ativo.collidepoint(mouse_x, mouse_y):
                item_hover = item_ativo
                item_hover_pos = (ativo_x, ativo_y)

        #carta de item
        if item_hover:
            carta_x = 1300
            carta_y = 160

            carta_img = self.carta_imgs.get(item_hover.raridade, self.carta_imgs["comum"])
            self.screen.blit(carta_img, (carta_x, carta_y))

            
            fonte_nome = font.Font("assets/fontes/alagard.ttf", 20)
            fonte_desc = font.Font("assets/fontes/alagard.ttf", 16)

            
            icon_size = 80
            icon = transform.scale(item_hover.sprite, (icon_size, icon_size))
            icon_x = carta_x + (self.carta_imgs["comum"].get_width() - icon_size) // 2
            icon_y = carta_y + 50
            self.screen.blit(icon, (icon_x, icon_y))

            if isinstance(item_hover, ItemAtivo):
                for x in range(item_hover.usos):
                    draw.rect(self.screen, (0, 255, 0), (1340 + (x * 25), 483, 20, 8))

            
            texto_nome = fonte_nome.render(item_hover.nome, True, (0,0,0))
            nome_x = carta_x + (self.carta_imgs["comum"].get_width() - texto_nome.get_width()) // 2
            nome_y = icon_y + icon_size + 35
            self.screen.blit(texto_nome, (nome_x, nome_y))

            
            descricao = item_hover.descricao
            linhas = []
            palavras = descricao.split(" ")
            linha_atual = ""

            for palavra in palavras:
                test_line = linha_atual + " " + palavra if linha_atual else palavra
                if fonte_desc.size(test_line)[0] < 230:
                    linha_atual = test_line
                else:
                    linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)

            for i, linha in enumerate(linhas):
                texto_desc = fonte_desc.render(linha, True, (0,0,0))
                desc_x = carta_x + (self.carta_imgs["comum"].get_width() - texto_desc.get_width()) // 2
                desc_y = nome_y + 55 + i * 24
                self.screen.blit(texto_desc, (desc_x, desc_y))

        
        # Exibir a carta da arma
        arma = self.player.arma
        if hasattr(arma, "carta"):
            carta_img = image.load(arma.carta).convert_alpha()
            fator_escala = (self.item_width + 40) / 53  # manter proporção original
            nova_largura = int(53 * fator_escala)
            nova_altura = int(72 * fator_escala)
            carta_escalada = transform.scale(carta_img, (nova_largura, nova_altura))
            self.screen.blit(carta_escalada, (365, 160))  # ajuste a posição como quiser


        # --- ATRIBUTOS DA ARMA ---
        if self.player.arma:
            arma = self.player.arma
            fonte_attr = font.Font("assets/fontes/alagard.ttf", 32)
            cor_attr = (253, 246, 225)

            atributos = [
                f"Dano: {round(arma.dano, 1)}",
                f"Rapidez: {round(arma.velocidade, 1)}",
                f"Roubo de Vida: {round(arma.lifeSteal, 1)}",
                f"% Crítico: {round(arma.chanceCritico, 1)}",
                f"Dano Crítico: {round(arma.danoCriticoMod * arma.dano, 1)}",  # dano total crítico
                f"Mod: {arma.modificador.nome if hasattr(arma, 'modificador') else 'Nenhum'}"
            ]

            base_x = 365   # posição x na tela
            base_y = 640  # posição y inicial

            for i, linha in enumerate(atributos):
                texto = fonte_attr.render(linha, True, cor_attr)
                self.screen.blit(texto, (base_x, base_y + i * 48))

        # --- ATRIBUTOS DO PLAYER ---
        if self.player:
            player = self.player
            fonte_attr = font.Font("assets/fontes/alagard.ttf", 32)
            cor_attr = (253, 246, 225)

            atributos = [
                f'Força: {round(player.atributos["forca"], 1)}',
                f'Destreza: {round(player.atributos["destreza"], 1)}',
                f'Agilidade: {round(player.atributos["agilidade"], 1)}',
                f'Vigor: {round(player.atributos["vigor"], 1)}',
                f'Resistência: {round(player.atributos["resistencia"], 1)}',  # dano total crítico
                f'Estamina: {round(player.atributos["estamina"], 1)}',
                f'Sorte: {round(player.atributos["sorte"], 1)}'
            ]

            base_x = 1300   # posição x na tela
            base_y = 640  # posição y inicial

            for i, linha in enumerate(atributos):
                texto = fonte_attr.render(linha, True, cor_attr)
                self.screen.blit(texto, (base_x, base_y + i * 42))
