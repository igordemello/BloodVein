from pygame import *
import sys
from pygame.locals import QUIT
import math

class Colisao:
    def __init__(self, mapa, player, inimigos):
        self.mapa = mapa
        self.player = player
        self.inimigos = inimigos

    def checar_colisoes(self):
        self._colisao_player_mapa()
        self._colisao_player_inimigos()

    #underline na frente = função privada
    def _colisao_player_mapa(self):
        #print(self.mapa.get_colliders())
        for collider in self.mapa.get_colliders():
            # print(collider)
            #print(self.player.get_hitbox().colliderect(collider))
            #print(f'Hitbox do player: {self.player.get_hitbox()}')
            if self.player.get_hitbox().colliderect(collider):
                #print('bateu')
                self.player.voltar_posicao()

    def _colisao_player_inimigos(self):
        for inimigo in self.inimigos:
            if self.player.get_hitbox().colliderect(inimigo.get_hitbox()):
                self.player.voltar_posicao()
            if inimigo.get_hitbox().colliderect(self.player.get_hitbox()):
                inimigo.voltar_posicao()
