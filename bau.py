from pygame import *
from pygame.math import Vector2
from efeito import *
from itensDic import ConjuntoItens
from random import sample
from botao import Botao

class Bau:
    def __init__(self, conjunto: ConjuntoItens):
        self.itensDisp = conjunto
        self.ids_disponiveis = list(conjunto.itens_por_id)
        self.ids_sorteados = sample(self.ids_disponiveis, 3)
        self.itens_sorteados = [self.itensDisp.itens_por_id[id_] for id_ in self.ids_sorteados]
        self.font = font.Font('assets/Fontes/Philosopher-BoldItalic.ttf', 24)
        self.fontDesc = font.Font('assets/Fontes/Philosopher-Italic.ttf', 24)

        self.botoes = []
        self.estados_hover = [Vector2(1.0, 0.0) for _ in self.itens_sorteados]

        self.image_fundo = Surface((375, 500), SRCALPHA)
        self.image_fundo.fill((0, 0, 0, 0))


        for i in range(len(self.itens_sorteados)):
            x = 350 + 400 * i + 375 // 2
            y = 400 + 500 // 2
            botao = Botao(
                image=self.image_fundo,
                pos=(x, y),
                text_input="",
                font=self.font,
                base_color=(255, 255, 255),
                hovering_color=(0, 0, 0)
            )
            self.botoes.append(botao)

    def bauEscolherItens(self, tela):
        overlay = Surface(tela.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        mouse_pos = mouse.get_pos()

        for pos, item in enumerate(self.itens_sorteados):
            base_x = 350 + 400 * pos
            base_y = 300
            carta_width, carta_height = 375, 500
            carta_rect = Rect(base_x, base_y, carta_width, carta_height)

            # Detecta hover e faz interpolação
            is_hovered = carta_rect.collidepoint(mouse_pos)
            alvo = Vector2(1.1, -30) if is_hovered else Vector2(1.0, 0.0)
            self.estados_hover[pos] = self.estados_hover[pos].lerp(alvo, 0.1)

            scale = self.estados_hover[pos].x
            deslocamento_y = self.estados_hover[pos].y

            width = int(carta_width * scale)
            height = int(carta_height * scale)
            pos_x = base_x + carta_width // 2 - width // 2
            pos_y = base_y + deslocamento_y

            sprite_raridade = image.load(f"assets/itens/carta_{item.raridade}.png").convert_alpha()
            sprite_carta = transform.scale(sprite_raridade, (width, height))
            tela.blit(sprite_carta, (pos_x, pos_y))

            sprite_item = transform.scale(item.sprite, (int(128 * scale), int(128 * scale)))
            item_center_x = pos_x + width // 2 - sprite_item.get_width() // 2
            tela.blit(sprite_item, (item_center_x, pos_y + int(40 * scale)))

            # Nome centralizado e mais próximo do item
            titulo = self.font.render(item.nome, True, (0, 0, 0))
            titulo_rect = titulo.get_rect(center=(pos_x + width // 2, pos_y + 20 + int(height * 0.42)))
            tela.blit(titulo, titulo_rect)

            # Descrição centralizada linha por linha (ajustada para não passar das margens)
            max_largura_texto = width - 70
            descricao_linhas = self.quebrar_texto_em_linhas(item.descricao, self.fontDesc, max_largura_texto)
            y_base = pos_y + int(height * 0.52)
            for i, linha in enumerate(descricao_linhas):
                texto = self.fontDesc.render(linha, True, (0, 0, 0))
                texto_rect = texto.get_rect(center=(pos_x + width // 2, y_base + 50+ i * 24))
                tela.blit(texto, texto_rect)

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
                linhas.append(linha_atual)
                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)

        return linhas

    def checar_clique_bau(self, mouse_pos):
        for i, botao in enumerate(self.botoes):
            if botao.checkForInput(mouse_pos):
                item_escolhido = self.itens_sorteados[i]
                print(f"Item escolhido: {item_escolhido.nome}")
                return item_escolhido
        return None