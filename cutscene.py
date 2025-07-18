from pygame import *
import sys
from pygame.locals import QUIT
from utils import resource_path 
class Cutscene:
    def __init__(self, cenas, fundo_surface, largura_tela, altura_tela):
        self.cenas = cenas
        self.index = 0
        self.ativa = True
        self.fundo = fundo_surface
        self.screen_w = largura_tela
        self.screen_h = altura_tela

        self.personagem_img = None
        self.personagem_x = 0
        self.velocidade = 20

        self.dialogo_font = font.Font(resource_path('assets/Fontes/alagard.ttf'),24)
        self.caixa_dialogo = Surface((largura_tela - 500, 100))

        self.caixa_dialogo.fill((243, 236, 215))

        self._carregar_cena_atual()

    def _carregar_cena_atual(self):
        cena = self.cenas[self.index]
        self.fala = cena["fala"]
        self.lado = cena.get("lado", "direita")
        self.personagem_img = cena["imagem"]

        if self.lado == "esquerda":
            self.personagem_x = -self.personagem_img.get_width()
            self.destino_x = -175
        else:
            self.personagem_x = self.screen_w
            self.destino_x = self.screen_w - self.personagem_img.get_width() +175

    def update(self, eventos):
        if not self.ativa:
            return
        
        for event in eventos:
            if event.type == KEYDOWN and event.key == K_SPACE:
                if self.personagem_x == self.destino_x:
                    self.index += 1
                    if self.index >= len(self.cenas):
                        self.ativa = False
                    else:
                        self._carregar_cena_atual()

        if self.personagem_x < self.destino_x:
            self.personagem_x = min(self.destino_x, self.personagem_x + self.velocidade)
        elif self.personagem_x > self.destino_x:
            self.personagem_x = max(self.destino_x, self.personagem_x - self.velocidade)

    def draw(self, screen):
        if not self.ativa:
            return
        
        escurecedor = Surface((self.screen_w, self.screen_h))
        escurecedor.set_alpha(100)
        escurecedor.fill((0, 0, 0))
        screen.blit(self.fundo, (0, 0))
        screen.blit(escurecedor, (0, 0))

        screen.blit(self.personagem_img, (self.personagem_x, self.screen_h - self.personagem_img.get_height() - 50))

        caixa_largura = self.screen_w - 500
        caixa_altura = 100
        caixa_x = (self.screen_w - caixa_largura) // 2
        caixa_y = self.screen_h - caixa_altura - 30
        espessura_borda = 6

        draw.rect(screen, (212, 175, 55), Rect(caixa_x - espessura_borda, caixa_y - espessura_borda,caixa_largura + 2 * espessura_borda, caixa_altura + 2 * espessura_borda),border_radius=24)
        draw.rect(screen, (243, 236, 215), Rect(caixa_x, caixa_y, caixa_largura, caixa_altura), border_radius=20)


        fala_render = self.dialogo_font.render(self.fala, True, (26,26,26))
        texto_w = fala_render.get_width()
        texto_h = fala_render.get_height()

        texto_x = caixa_x + (caixa_largura - texto_w) // 2
        texto_y = caixa_y + (caixa_altura - texto_h) // 2

        screen.blit(fala_render, (texto_x, texto_y))