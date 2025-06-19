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
        self.tela = tela
        self.mapa = Mapa(caminho_mapa,self.tela,self.tela.get_width(),self.tela.get_height())
        self.inimigos = [Orb(400,700,64,64)]
        self.colisao = Colisao(self.mapa, player, self.inimigos)
        self.porta_liberada = False
        self.player = player
        self.ranges_doors = self.mapa.get_rangesdoors() 
        self.proxima_sala = f"mapas/sala_{1}.tmx"

        self.colliders = self.mapa.get_colliders()

    def atualizar(self,dt,teclas):
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.atualizar((self.player.x,self.player.y), self.tela)
                #da o dano no jogador
                inimigo.dar_dano = lambda val=inimigo.dano: self.player.tomar_dano(val)
        
        self.colisao.checar_colisoes(self.player,self.inimigos, teclas,dt)

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
        
        #debug visual das colisões do player e do mapa:
        # for collider in self.mapa.get_colliders():
        #     draw.rect(tela, (255,0,0), collider['rect'], 1)
        # draw.rect(tela, (0,255,0), self.player.player_rect, 2)


    def pode_trocar_de_sala(self):
        return self.porta_liberada and any(self.player.get_hitbox().colliderect(rangee) for rangee in self.ranges_doors)