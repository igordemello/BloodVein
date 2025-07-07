from pygame import *
from pygame.math import Vector2
from efeito import *
from hud import Hud
from itensDic import ConjuntoItens
from random import sample
from botao import Botao
from armas import *
from player import Player



class MenuArmas:
    def __init__(self, hud):
        self.lista_mods = ListaMods()
        self.hud = hud

        # Armamentos disponíveis
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

        self.atributosFundo = image.load("assets/ui/atributo_fundo.png").convert_alpha()
        self.armasFundo = image.load("assets/ui/armas_fundo.png").convert_alpha()

        # Estados do menu
        self.menu_ativo = False
        self.tela_atual = "atributos"  # "atributos" ou "armas"
        self.arma_escolhida = None

        # Atributos do jogador
        self.atributos = {
            "forca": 5,
            "destreza": 5,
            "agilidade": 5,
            "vigor": 5,
            "resistencia": 5,
            "estamina": 5,
            "sorte": 5
        }
        self.pontos_totais = 10
        self.pontos_usados = 7
        self.botoes_atributos = {}

        # Traits system
        self.traits = [
            "Vampira",
            "Translúcido",
            "Peçonhento",
            "Mercúrio",
            "Ancião",
            "Humano"
        ]
        self.trait_selecionada = 0
        self.botoes_traits = {}

        # Botões de navegação
        screen_width, screen_height = display.get_surface().get_size()
        self.botao_prosseguir = Botao(
            image=None,
            pos=(screen_width - 400, screen_height - 100),
            text_input="SELECIONAR ARMA",
            font=font.Font('assets/Fontes/alagard.ttf', 58),
            base_color=(255, 255, 255),
            hovering_color=(200, 200, 200)
        )

        self.botao_voltar = Botao(
            image=None,
            pos=(200, screen_height - 100),
            text_input="VOLTAR",
            font=font.Font('assets/Fontes/alagard.ttf', 58),
            base_color=(255, 255, 255),
            hovering_color=(200, 200, 200)
        )

        self.botao_iniciar = Botao(
            image=None,
            pos=(screen_width // 2 + 800, screen_height - 100),
            text_input="INICIAR",
            font=font.Font('assets/Fontes/alagard.ttf', 58),
            base_color=(255, 255, 255),
            hovering_color=(200, 200, 200)
        )

    def tela_atributos(self, tela):
        tela.blit(self.atributosFundo, (0, 0))

        atributos_width = int(tela.get_width() * 0.5)
        atributos_height = int(tela.get_height() * 0.75)
        atributos_bg = Surface((atributos_width, atributos_height), SRCALPHA)
        atributos_bg.fill((0, 0, 0, 150))
        atributos_bg_rect = atributos_bg.get_rect(center=(665, tela.get_height() // 2 + 100))
        tela.blit(atributos_bg, atributos_bg_rect)

        # Atributos
        y_pos = 300
        mouse_pos = mouse.get_pos()
        font_atributos = font.Font('assets/Fontes/alagard.ttf', 48)

        for nome, valor in self.atributos.items():
            nome_texto = font_atributos.render(nome.capitalize() + ":", True, (255, 255, 255))
            tela.blit(nome_texto, (635 - 300, y_pos))

            valor_texto = font_atributos.render(str(valor), True, (255, 255, 255))
            tela.blit(valor_texto, (635 + 215, y_pos))

            # Botão -
            botao_menos_rect = Rect(635 + 100, y_pos, 48, 48)
            draw.rect(tela, (200, 0, 0) if botao_menos_rect.collidepoint(mouse_pos) else (150, 0, 0), botao_menos_rect)
            menos_texto = font_atributos.render("-", True, (255, 255, 255))
            tela.blit(menos_texto, (botao_menos_rect.x + 10, botao_menos_rect.y - 5))

            # Botão +
            botao_mais_rect = Rect(635 + 300, y_pos, 48, 48)
            draw.rect(tela, (0, 200, 0) if botao_mais_rect.collidepoint(mouse_pos) else (0, 150, 0), botao_mais_rect)
            mais_texto = font_atributos.render("+", True, (255, 255, 255))
            tela.blit(mais_texto, (botao_mais_rect.x + 10, botao_mais_rect.y))

            self.botoes_atributos[f"{nome}_menos"] = botao_menos_rect
            self.botoes_atributos[f"{nome}_mais"] = botao_mais_rect

            y_pos += 70

        # Pontos disponíveis
        pontos_texto = font.Font('assets/Fontes/alagard.ttf', 36).render(
            f"Pontos: {self.pontos_usados}/{self.pontos_totais}",
            True,
            (255, 255, 255) if self.pontos_usados <= self.pontos_totais else (255, 0, 0)
        )
        tela.blit(pontos_texto, (635 - pontos_texto.get_width() // 2, y_pos + 20))

        # Traits
        y_pos += 105
        traits_titulo = font.Font('assets/Fontes/alagard.ttf', 48).render("TRAÇO SELECIONADO", True, (255, 255, 255))
        tela.blit(traits_titulo, (635 - traits_titulo.get_width() // 2, y_pos))

        y_pos += 90
        trait_font = font.Font('assets/Fontes/alagard.ttf', 32)
        trait_text = trait_font.render(self.traits[self.trait_selecionada], True, (255, 255, 255))
        trait_rect = trait_text.get_rect(center=(635, y_pos))
        tela.blit(trait_text, trait_rect)

        #fundos


        # Setas para navegar entre traits
        seta_esquerda = image.load("assets/UI/seta_esquerda.png").convert_alpha()
        seta_direita = image.load("assets/UI/seta_direita.png").convert_alpha()

        seta_esq_rect = seta_esquerda.get_rect(center=(635 - 200, y_pos))
        seta_dir_rect = seta_direita.get_rect(center=(635 + 200, y_pos))

        tela.blit(seta_esquerda, seta_esq_rect)
        tela.blit(seta_direita, seta_dir_rect)

        self.botoes_traits["trait_esquerda"] = seta_esq_rect
        self.botoes_traits["trait_direita"] = seta_dir_rect

        # Botão para prosseguir
        self.botao_prosseguir.changeColor(mouse_pos)
        self.botao_prosseguir.update(tela)

    def tela_armas(self, tela):
        tela.blit(self.armasFundo, (0, 0))

        mouse_pos = mouse.get_pos()
        carta_width, carta_height = 375, 500
        scale_central = 1.0
        scale_lateral = 0.7
        opacity_lateral = 150

        arma_anterior = self.armasDisp[self.pos - 1] if self.pos > 0 else self.armasDisp[-1]
        arma_atual = self.armasDisp[self.pos]
        arma_proxima = self.armasDisp[self.pos + 1] if self.pos < len(self.armasDisp) - 1 else self.armasDisp[0]

        center_x = tela.get_width() // 2 + 200
        center_y = tela.get_height() // 2
        offset_x = 220

        cartas = [
            {"arma": arma_anterior, "x": center_x - offset_x, "y": center_y, "scale": scale_lateral,
             "opacity": opacity_lateral, "z_index": 1},
            {"arma": arma_atual, "x": center_x, "y": center_y, "scale": scale_central, "opacity": 255, "z_index": 2},
            {"arma": arma_proxima, "x": center_x + offset_x, "y": center_y, "scale": scale_lateral,
             "opacity": opacity_lateral, "z_index": 1}
        ]

        for carta in sorted(cartas, key=lambda x: x["z_index"]):
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

            arma = carta['arma']
            if hasattr(arma, "carta"):
                carta_img = image.load(arma.carta).convert_alpha()
                sprite_carta = transform.scale(carta_img, (width, height))

            if carta["opacity"] < 255:
                sprite_carta.fill((255, 255, 255, carta["opacity"]), special_flags=BLEND_RGBA_MULT)

            tela.blit(sprite_carta, (pos_x, pos_y))

        # Setas de navegação
        seta_esquerda = image.load("assets/UI/seta_esquerda.png").convert_alpha()
        seta_direita = image.load("assets/UI/seta_direita.png").convert_alpha()

        seta_esq_rect = seta_esquerda.get_rect(center=(center_x - offset_x - 150, center_y))
        seta_dir_rect = seta_direita.get_rect(center=(center_x + offset_x + 150, center_y))

        tela.blit(seta_esquerda, seta_esq_rect)
        tela.blit(seta_direita, seta_dir_rect)

        # Botões de navegação
        self.botao_voltar.changeColor(mouse_pos)
        self.botao_voltar.update(tela)

        self.botao_iniciar.changeColor(mouse_pos)
        self.botao_iniciar.update(tela)

    def menuEscolherItens(self, tela):
        if self.tela_atual == "atributos":
            self.tela_atributos(tela)
        elif self.tela_atual == "armas":
            self.tela_armas(tela)

    def checar_clique_menu(self, mouse_pos):
        if self.tela_atual == "atributos":
            # Verifica cliques nos botões de atributos
            for nome, rect in self.botoes_atributos.items():
                if rect.collidepoint(mouse_pos):
                    atributo = nome.split("_")[0]
                    operacao = nome.split("_")[1]

                    if operacao == "menos" and self.atributos[atributo] > 1:
                        self.atributos[atributo] -= 1
                        self.pontos_usados -= 1
                    elif operacao == "mais" and self.atributos[atributo] < 10:
                        if self.pontos_usados < self.pontos_totais:
                            self.atributos[atributo] += 1
                            self.pontos_usados += 1
                    return None

            # Verifica cliques nas setas de traits
            for nome, rect in self.botoes_traits.items():
                if rect.collidepoint(mouse_pos):
                    if nome == "trait_esquerda":
                        self.trait_selecionada = (self.trait_selecionada - 1) % len(self.traits)
                    elif nome == "trait_direita":
                        self.trait_selecionada = (self.trait_selecionada + 1) % len(self.traits)
                    return None

            # Verifica clique no botão de prosseguir
            if self.botao_prosseguir.checkForInput(mouse_pos):
                self.tela_atual = "armas"
                return None

        elif self.tela_atual == "armas":
            center_x = display.get_surface().get_width() // 2
            center_y = display.get_surface().get_height() // 2
            offset_x = 220

            carta_rect = Rect(0, 0, 375, 500)
            carta_rect.center = (center_x, center_y)

            seta_esquerda_rect = Rect(0, 0, 64, 64)
            seta_esquerda_rect.center = (center_x - offset_x - 150, center_y)

            seta_direita_rect = Rect(0, 0, 64, 64)
            seta_direita_rect.center = (center_x + offset_x + 150, center_y)

            if carta_rect.collidepoint(mouse_pos):
                return None
            elif seta_esquerda_rect.collidepoint(mouse_pos):
                self.scrollMenu("<")
            elif seta_direita_rect.collidepoint(mouse_pos):
                self.scrollMenu(">")
            elif self.botao_voltar.checkForInput(mouse_pos):
                self.tela_atual = "atributos"
                return None
            elif self.botao_iniciar.checkForInput(mouse_pos):
                self.menu_ativo = False
                # Aplica modificador antes de retornar a arma
                self.arma_sorteada.aplicaModificador()
                return self.arma_sorteada, self.atributos.copy(), self.traits[self.trait_selecionada]

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