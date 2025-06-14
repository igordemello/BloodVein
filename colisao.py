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
        #self._colisao_inimgos_mapa()

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
            if inimigo.hp <= 0:
                inimigo.vivo = False
                return
            if self.player.get_hitbox().colliderect(inimigo.get_hitbox()):
                self.player.voltar_posicao()
            if inimigo.get_hitbox().colliderect(self.player.get_hitbox()):
                inimigo.voltar_posicao()

    # colisão entre o inimigo e o mapa, porém atualmente a IA de seguir o personagem não prevê esse tipo de coisa,
    # então o inimigo fica agarrado. Descomentar no checar_colisoes quando descomentar aqui
    # def _colisao_inimgos_mapa(self):
    #     for collider in self.mapa.get_colliders():
    #         for inimigo in self.inimigos:
    #             if inimigo.get_hitbox().colliderect(collider):
    #                 inimigo.voltar_posicao()
