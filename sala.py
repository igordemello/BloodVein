from pygame import *
import sys
from pygame.locals import QUIT
import math
from mapa import Mapa
from inimigos.orb import Orb
from colisao import Colisao

init()
fonte = font.SysFont("Arial", 24)

class Sala:
    def __init__(self, caminho_mapa, tela, player):
        self.mapa = Mapa(caminho_mapa,tela,tela.get_width(),tela.get_height())
        self.inimigos = [Orb(400,700,64,64)]
        self.colisao = Colisao(self.mapa, player, self.inimigos)
        self.porta_liberada = False
        self.player = player
        self.ranges_doors = self.mapa.get_rangesdoors() 
        self.proxima_sala = f"mapas/sala_{1}.tmx"

    def atualizar(self,dt,teclas):
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.atualizar((self.player.x,self.player.y))
        
        self.colisao.checar_colisoes(self.player,self.inimigos, teclas)

        if not any(inimigo.vivo for inimigo in self.inimigos):
            self.porta_liberada = True

    def desenhar(self, tela):
        self.mapa.desenhar(self.porta_liberada)
        for inimigo in self.inimigos:
            if inimigo.vivo:
                    inimigo.desenhar(tela, (self.player.x,self.player.y))
        

        if self.pode_trocar_de_sala():
            texto = fonte.render(f"Aperte E para trocar de sala", True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(960,1050))
            tela.blit(texto, texto_rect)


    def pode_trocar_de_sala(self):
        return self.porta_liberada and any(self.player.get_hitbox().colliderect(rangee) for rangee in self.ranges_doors)