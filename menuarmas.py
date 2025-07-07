from pygame import *
from pygame.math import Vector2
from efeito import *
from hud import Hud
from itensDic import ConjuntoItens
from random import sample
from botao import Botao
from armas import *


class MenuArmas:
    def __init__(self, hud):
        self.lista_mods = ListaMods()
        self.hud = hud
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

        for i in self.armasDisp:
            i.aplicaModificador()

        self.pos = 0
        self.arma_sorteada = self.armasDisp[self.pos]
        self.font = font.Font('assets/Fontes/alagard.ttf', 18)
        self.fontDesc = font.Font('assets/Fontes/alagard.ttf', 18)
        self.fontTitulo = font.Font('assets/Fontes/alagard.ttf', 72)
        self.fontAtributos = font.Font('assets/Fontes/alagard.ttf', 24)

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

        # Atributos do jogador
        self.atributos = {
            "forca": 1,
            "destreza": 1,
            "agilidade": 1,
            "vigor": 1,
            "resistencia": 1,
            "estamina": 1,
            "sorte": 1
        }
        self.pontos_totais = 10  # Total de pontos disponíveis
        self.pontos_usados = 7  # 1 ponto por atributo inicial
        self.botoes_atributos = {}

    def desenhaAtributos(self, tela):
        # Variáveis para tamanho das fontes
        TAMANHO_FONTE_ATRIBUTOS = 56  # Tamanho da fonte para os atributos
        TAMANHO_FONTE_PONTOS = 36  # Tamanho da fonte para os pontos restantes

        atributos_width = int(tela.get_width() * 0.4)
        atributos_bg = Surface((atributos_width, tela.get_height()), SRCALPHA)
        atributos_bg.fill((0, 0, 0, 150))
        tela.blit(atributos_bg, (0, 0))

        # Título "ATRIBUTOS" (mantém fonte original)
        atributos_titulo = self.fontTitulo.render("ATRIBUTOS", False, (255, 255, 255))
        tela.blit(atributos_titulo, (215, 40))

        # Posição inicial para desenhar os atributos
        y_pos = 150
        mouse_pos = mouse.get_pos()

        # Cria fontes
        font_atributos = font.Font('assets/Fontes/alagard.ttf', TAMANHO_FONTE_ATRIBUTOS)
        font_pontos = font.Font('assets/Fontes/alagard.ttf', TAMANHO_FONTE_PONTOS)

        for nome, valor in self.atributos.items():
            # Desenha o nome do atributo
            nome_texto = font_atributos.render(nome.capitalize() + ":", True, (255, 255, 255))
            tela.blit(nome_texto, (80, y_pos))

            # Desenha o valor do atributo
            valor_texto = font_atributos.render(str(valor), True, (255, 255, 255))
            tela.blit(valor_texto, (555, y_pos))

            # Botão para diminuir (-)
            botao_menos_rect = Rect(440, y_pos, 48, 48)
            draw.rect(tela, (200, 0, 0) if botao_menos_rect.collidepoint(mouse_pos) else (150, 0, 0), botao_menos_rect)
            menos_texto = font_atributos.render("-", True, (255, 255, 255))
            tela.blit(menos_texto, (453, y_pos - 5))

            # Botão para aumentar (+)
            botao_mais_rect = Rect(640, y_pos, 48, 48)
            draw.rect(tela, (0, 200, 0) if botao_mais_rect.collidepoint(mouse_pos) else (0, 150, 0), botao_mais_rect)
            mais_texto = font_atributos.render("+", True, (255, 255, 255))
            tela.blit(mais_texto, (647, y_pos))

            # Armazena os retângulos dos botões para verificação de clique
            self.botoes_atributos[f"{nome}_menos"] = botao_menos_rect
            self.botoes_atributos[f"{nome}_mais"] = botao_mais_rect

            y_pos += 90

        # Mostra pontos disponíveis (usando fonte específica)
        pontos_texto = font_pontos.render(
            f"Pontos: {self.pontos_usados}/{self.pontos_totais}",
            True,
            (255, 255, 255) if self.pontos_usados <= self.pontos_totais else (255, 0, 0)
        )
        tela.blit(pontos_texto, (470, y_pos + 5))

    def menuEscolherItens(self, tela):
        overlay = Surface(tela.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        mouse_pos = mouse.get_pos()
        carta_width, carta_height = 375, 500
        scale_central = 1.0
        scale_lateral = 0.7
        opacity_lateral = 150

        arma_anterior = self.armasDisp[self.pos - 1] if self.pos > 0 else self.armasDisp[-1]
        arma_atual = self.armasDisp[self.pos]
        arma_proxima = self.armasDisp[self.pos + 1] if self.pos < len(self.armasDisp) - 1 else self.armasDisp[0]

        center_x = tela.get_width() * 0.75
        center_y = tela.get_height() // 2
        offset_x = 220

        # Lista de cartas ordenadas por profundidade (renderizar da esquerda para a direita)
        cartas = [
            {"arma": arma_anterior, "x": center_x - offset_x, "y": center_y, "scale": scale_lateral,
             "opacity": opacity_lateral, "z_index": 1},
            {"arma": arma_atual, "x": center_x, "y": center_y, "scale": scale_central, "opacity": 255, "z_index": 2},
            # Prioridade máxima
            {"arma": arma_proxima, "x": center_x + offset_x, "y": center_y, "scale": scale_lateral,
             "opacity": opacity_lateral, "z_index": 1}
        ]

        # Renderiza as cartas em ordem correta (evita sobreposição incorreta)
        for carta in sorted(cartas, key=lambda x: x["z_index"]):  # Ordena da esquerda para a direita
            carta_rect = Rect(0, 0, carta_width * carta["scale"], carta_height * carta["scale"])
            carta_rect.center = (carta["x"], carta["y"])

            if carta["arma"] == arma_atual:
                is_hovered = carta_rect.collidepoint(mouse_pos)
                alvo = Vector2(1.1, -30) if is_hovered else Vector2(1.0, 0)
                self.estado_hover = self.estado_hover.lerp(alvo, 0.1)
                scale = self.estado_hover.x * carta["scale"]
                deslocamento_y = self.estado_hover.y

                if is_hovered:
                    if not self.hud.stats_alpha:
                        self.hud.reset_stats_fade()
                    self.hud.mostraStatsArma(arma_atual)
            else:
                scale = carta["scale"]
                deslocamento_y = 0

            width = int(carta_width * scale)
            height = int(carta_height * scale)
            pos_x = carta["x"] - width // 2
            pos_y = carta["y"] - height // 2 + deslocamento_y

            sprite_raridade = image.load(f"assets/itens/carta_{carta['arma'].raridadeStr}.png").convert_alpha()
            sprite_carta = transform.scale(sprite_raridade, (width, height))

            if carta["opacity"] < 255:
                sprite_carta.fill((255, 255, 255, carta["opacity"]), special_flags=BLEND_RGBA_MULT)

            tela.blit(sprite_carta, (pos_x, pos_y))

            spriteIcon = image.load(carta['arma'].spriteIcon).convert_alpha()
            sprite_arma = transform.scale(spriteIcon, (int(128 * scale), int(128 * scale)))

            # Aplica opacidade ao ícone também
            if carta["opacity"] < 255:
                sprite_arma.fill((255, 255, 255, carta["opacity"]), special_flags=BLEND_RGBA_MULT)

            arma_center_x = pos_x + width // 2 - sprite_arma.get_width() // 2
            tela.blit(sprite_arma, (arma_center_x, pos_y + int(40 * scale)))

            titulo = self.font.render(carta['arma'].nome, True, (0, 0, 0))
            titulo_rect = titulo.get_rect(center=(pos_x + width // 2, pos_y + 20 + int(height * 0.42)))

            # Aplica opacidade ao título
            if carta["opacity"] < 255:
                titulo.set_alpha(carta["opacity"])

            tela.blit(titulo, titulo_rect)

        # Desenha os atributos do jogador
        self.desenhaAtributos(tela)

        # Título "ARMAS"
        armasTitulo = self.fontTitulo.render("ARMAS", False, (255, 255, 255))
        tela.blit(armasTitulo, (1320, 40, 24, 24))

        # Setas de navegação
        seta_esquerda = image.load("assets/UI/seta_esquerda.png").convert_alpha()
        seta_direita = image.load("assets/UI/seta_direita.png").convert_alpha()

        seta_esq_rect = seta_esquerda.get_rect(center=(center_x - offset_x - 150, center_y))
        seta_dir_rect = seta_direita.get_rect(center=(center_x + offset_x + 150, center_y))

        tela.blit(seta_esquerda, seta_esq_rect)
        tela.blit(seta_direita, seta_dir_rect)

    def checar_clique_menu(self, mouse_pos):
        screen_width = display.get_surface().get_width()
        center_x = screen_width * 0.75
        center_y = display.get_surface().get_height() // 2
        offset_x = 220

        carta_rect = Rect(0, 0, 375, 500)
        carta_rect.center = (center_x, center_y)

        seta_esquerda_rect = Rect(0, 0, 64, 64)
        seta_esquerda_rect.center = (center_x - offset_x - 150, center_y)

        seta_direita_rect = Rect(0, 0, 64, 64)
        seta_direita_rect.center = (center_x + offset_x + 150, center_y)

        # Verifica cliques nos botões de atributos
        for nome, rect in self.botoes_atributos.items():
            if rect.collidepoint(mouse_pos):
                atributo = nome.split("_")[0]
                operacao = nome.split("_")[1]

                if operacao == "menos" and self.atributos[atributo] > 1:
                    self.atributos[atributo] -= 1
                    self.pontos_usados -= 1
                elif operacao == "mais" and self.atributos[atributo] < 17:
                    # Verifica se há pontos disponíveis
                    if self.pontos_usados < self.pontos_totais:
                        self.atributos[atributo] += 1
                        self.pontos_usados += 1
                return None

        if carta_rect.collidepoint(mouse_pos):
            print(f"Arma escolhida: {self.arma_sorteada.nome}")
            print("Atributos selecionados:")
            for nome, valor in self.atributos.items():
                print(f"{nome.capitalize()}: {valor}")
            self.menu_ativo = False

            # Retorna tanto a arma quanto os atributos selecionados
            return self.arma_sorteada, self.atributos.copy()
        elif seta_esquerda_rect.collidepoint(mouse_pos):
            self.scrollMenu("<")
        elif seta_direita_rect.collidepoint(mouse_pos):
            self.scrollMenu(">")

        return None

    def scrollMenu(self, input):
        if input == ">":
            if self.pos == len(self.armasDisp) - 1:
                self.pos = 0
            else:
                self.pos += 1
        else:
            if self.pos == 0:
                self.pos = len(self.armasDisp) - 1
            else:
                self.pos -= 1

        self.arma_sorteada = self.armasDisp[self.pos]