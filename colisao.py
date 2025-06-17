from pygame import *
import sys
from pygame.locals import QUIT
import math

class Colisao:
    def __init__(self, mapa, player, inimigos):
        self.mapa = mapa
        self.player = player
        self.inimigos = inimigos

    def checar_colisoes(self,player,inimigos, teclas,dt):
        self._colisao_player_mapa(teclas,dt)
        self._colisao_player_inimigos()
        #self._colisao_inimgos_mapa()
        self._colisao_inimigos_inimigos()

    def checar_mask_collision(self, r1,m1,r2,m2):
        if not r1.colliderect(r2):
            return False
        offset = (r2.x - r1.x, r2.y - r1.y)
        return m1.overlap(m2, offset)

    #underline na frente = função privada
    def _colisao_player_mapa(self, keys,dt):
        dx = dy = 0
        
        speed = self.player.velocidadeMov * dt # 3 é a escala do mapa
    
        if keys[K_a]: dx = -speed
        if keys[K_d]: dx = speed
        if keys[K_w]: dy = -speed
        if keys[K_s]: dy = speed

        # Cria rect temporário para teste
        new_rect = self.player.player_rect.copy()
        
        # Testa movimento em X
        new_rect.x += dx
        can_move_x = True
        for collider in self.mapa.get_colliders():
            if new_rect.colliderect(collider['rect']):  # Simples colisão AABB primeiro
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_x = False
                break
        
        # Testa movimento em Y
        new_rect.x = self.player.player_rect.x  # Reseta X
        new_rect.y += dy
        can_move_y = True
        for collider in self.mapa.get_colliders():
            if new_rect.colliderect(collider['rect']):
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_y = False
                break

        # Aplica movimento
        final_x = self.player.player_rect.x + (dx if can_move_x else 0)
        final_y = self.player.player_rect.y + (dy if can_move_y else 0)
        self.player.player_rect.topleft = (final_x, final_y)

            
        

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
