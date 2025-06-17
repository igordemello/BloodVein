from pygame import *
import sys
from pygame.locals import QUIT
import math

class Colisao:
    def __init__(self, mapa, player, inimigos):
        self.mapa = mapa
        self.player = player
        self.inimigos = inimigos

    def checar_colisoes(self,player,inimigos, teclas):
        self._colisao_player_mapa(teclas)
        self._colisao_player_inimigos()
        #self._colisao_inimgos_mapa()
        self._colisao_inimigos_inimigos()

    def checar_mask_collision(self, r1,m1,r2,m2):
        if not r1.colliderect(r2):
            return False
        offset = (r2.x - r1.x, r2.y - r1.y)
        return m1.overlap(m2, offset)

    #underline na frente = função privada
    def _colisao_player_mapa(self,keys):
        dx = dy = 0

        if  keys[K_a]:
            dx = -self.player.speedforcollision
        if keys[K_d]:
            dx = self.player.speedforcollision
        if keys[K_w]:
            dy = -self.player.speedforcollision
        if keys[K_s]:
            dy = self.player.speedforcollision

        
        colliders_and_masks = self.mapa.get_colliders()
        for collider_and_mask in colliders_and_masks:
            collider_rect = collider_and_mask['rect']
            collider_mask = collider_and_mask['mask']
            print(collider_rect)
            print(collider_mask)

            temp_rect = self.player.player_rect.move(dx, 0)
            if not self.checar_mask_collision(temp_rect, self.player.player_mask, collider_rect, collider_mask):
                self.player.mov_player(temp_rect)

            temp_rect = self.player.player_rect.move(0, dy)
            if not self.checar_mask_collision(temp_rect, self.player.player_mask, collider_rect, collider_mask):
                self.player.mov_player(temp_rect)

            
        

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

    def _colisao_inimigos_inimigos(self):
        for inimigo in self.inimigos:
            for inimigo2 in self.inimigos:
                if inimigo == inimigo2:
                    continue
                if inimigo.get_hitbox().colliderect(inimigo2.get_hitbox()):
                    inimigo.voltar_posicao()
                if inimigo2.get_hitbox().colliderect(inimigo.get_hitbox()):
                    inimigo2.voltar_posicao()
