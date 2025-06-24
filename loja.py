from pygame import *
from pygame.locals import QUIT
import sys
from random import sample
from botao import Botao
from itensDic import ConjuntoItens
from pygame.math import Vector2
import math

class Loja():
    def __init__(self, conjunto: ConjuntoItens, player):
        self.personagem_img = transform.scale(image.load('assets/iko.png').convert_alpha(), (750, 750))
        
        self.itensDisp = conjunto
        self.ids_disponiveis = list(conjunto.itens_por_id)
        self.ids_sorteados = sample(self.ids_disponiveis, 3)
        self.itens_sorteados = [self.itensDisp.itens_por_id[id_] for id_ in self.ids_sorteados]
        
        self.precos = {
            "comum": 15,
            "rara": 30,
            "lendaria": 45
        }
        
        self.player = player
        self.tempo = 0  # Para animação
        
        self.font_titulo = font.SysFont("Arial", 26, bold=True)
        self.font_desc = font.SysFont("Arial", 20)
        self.font_preco = font.SysFont("Arial", 24, bold=True)
        
        self.estados_hover = [Vector2(1.0, 0.0) for _ in self.itens_sorteados]
        self.descricao_visivel = [False] * 3
        
        self.botoes = []
        self.item_width, self.item_height = 300, 400
        
    
        # Carregar imagens de cartas por raridade
        self.carta_imgs = {
            "comum": transform.scale(image.load("assets/itens/carta_comum_loja.png").convert_alpha(), (self.item_width, self.item_height)),
            "rara": transform.scale(image.load("assets/itens/carta_rara_loja.png").convert_alpha(), (self.item_width, self.item_height)),
            "lendaria": transform.scale(image.load("assets/itens/carta_lendaria_loja.png").convert_alpha(), (self.item_width, self.item_height))
        }
        
        for i in range(3):
            x = 900 + i * 350
            y = 250
            botao = Botao(
                image=Surface((self.item_width, self.item_height), SRCALPHA),
                pos=(x + self.item_width//2, y + self.item_height//2),
                text_input="",
                font=self.font_titulo,
                base_color=(255, 255, 255),
                hovering_color=(200, 200, 200)
            )
            self.botoes.append(botao)

        self.comprado = [False]*3

    def desenhar_loja(self, tela):
        tela.fill((0, 0, 0))
        tela.blit(self.personagem_img, (50, 150))

        mouse_pos = mouse.get_pos()
        self.tempo += 0.05

        for pos, item in enumerate(self.itens_sorteados):

            #animação foda
            flutuacao = math.sin(self.tempo + pos * 2) * 10
            base_x = 900 + pos * 350
            base_y = 250 + flutuacao

            item_rect = Rect(base_x, base_y, self.item_width, self.item_height)
            is_hovered = item_rect.collidepoint(mouse_pos)
            self.descricao_visivel[pos] = is_hovered

            alvo = Vector2(1.05, -20) if is_hovered else Vector2(1.0, 0.0)
            self.estados_hover[pos] = self.estados_hover[pos].lerp(alvo, 0.1)

            scale = self.estados_hover[pos].x
            offset_y = self.estados_hover[pos].y

            width = int(self.item_width * scale)
            height = int(self.item_height * scale)
            pos_x = base_x + (self.item_width - width) // 2
            pos_y = base_y + offset_y

            # Desenhar imagem da carta de fundo
            carta_base = transform.scale(self.carta_imgs[item.raridade], (width, height))
            tela.blit(carta_base, (pos_x, pos_y))

            # Sprite do item
            item_img = transform.scale(item.sprite, (100, 100))
            tela.blit(item_img, (pos_x + (width - 100)//2, pos_y + 40))

            # Nome do item
            nome = self.font_titulo.render(item.nome, True, (255, 255, 255))
            tela.blit(nome, (pos_x + (width - nome.get_width())//2, pos_y + 173))

            # Preço
            preco = self.font_preco.render(f"{self.precos[item.raridade]} almas", True, (255, 215, 0))
            tela.blit(preco, (pos_x + (width - preco.get_width())//2,  200))

            #carta comprada
            if self.comprado[pos]:
                    carta_tchau = Surface((width, height), SRCALPHA)
                    carta_tchau.fill((151, 0, 0, 90))  # Preto com transparência
                    tela.blit(carta_tchau, (pos_x, pos_y))


            # Descrição (hover)
            if self.descricao_visivel[pos]:
                desc_lines = self.quebrar_texto_em_linhas(item.descricao, self.font_desc, width - 40)
                for i, line in enumerate(desc_lines):
                    desc_text = self.font_desc.render(line, True, (255, 255, 255))
                    tela.blit(desc_text, (pos_x + 27, pos_y + 240 + i * 22))

        for botao in self.botoes:
            botao.changeColor(mouse_pos)
            botao.update(tela)

    def quebrar_texto_em_linhas(self, texto, fonte, largura_max):
        palavras = texto.split()
        linhas = []
        linha_atual = ""
        
        for palavra in palavras:
            teste = linha_atual + (" " if linha_atual else "") + palavra
            if fonte.size(teste)[0] <= largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        
        if linha_atual:
            linhas.append(linha_atual)
        
        return linhas

    def checar_compra(self, mouse_pos, tela):
        for i, botao in enumerate(self.botoes):
            if botao.checkForInput(mouse_pos):
                item = self.itens_sorteados[i]
                preco = self.precos[item.raridade]

                if self.player.almas >= preco and not self.comprado[i]:
                    self.player.almas -= preco
                    self.player.adicionarItem(item)
                    comprado = self.font_preco.render("COMPRADO", True, ('Green'))
                    tela.blit(comprado, (0, 0))
                    self.comprado[i] = True
                    
                    return True
                else:
                    falta = self.font_preco.render("Faltam almas", True, ('red'))
                    tela.blit(falta, (0, 0))
                    return False