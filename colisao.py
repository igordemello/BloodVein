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
    
        if self.player.is_dashing:
            speed *= 3  #multiplicação do dash
            direcao = self.player.dash_direcao
            if direcao == 'a': dx = -speed
            elif direcao == 'd': dx = speed
            elif direcao == 'w': dy = -speed
            elif direcao == 's': dy = speed

            self.player.dash_duration += dt
            if self.player.dash_duration >= self.player.dash_duration_max:
                self.player.is_dashing = False
        else:
            if keys[K_a]: dx = -speed
            if keys[K_d]: dx = speed
            if keys[K_w]: dy = -speed
            if keys[K_s]: dy = speed



        new_rect = self.player.player_rect.copy()
        area_interesse = Rect( new_rect.x - 100, new_rect.y - 100, new_rect.width + 200, new_rect.height + 200)

        can_move_x,can_move_y = True,True

        new_rect.x += dx
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_x = False
                break
        

        new_rect.x = self.player.player_rect.x  #reseta x
        new_rect.y += dy
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_y = False
                break

        self.player.mover(can_move_x,can_move_y,dx,dy)

        # Aplica movimento
        # final_x = self.player.player_rect.x + (dx if can_move_x else 0)
        # final_y = self.player.player_rect.y + (dy if can_move_y else 0)
        # self.player.player_rect.topleft = (final_x, final_y)

            
        

    def _colisao_player_inimigos(self):
        for inimigo in self.inimigos:
            #if inimigo.hp <= 0:
            #    inimigo.vivo = False
            #    return
            if self.player.get_hitbox().colliderect(inimigo.get_hitbox()):
                self.player.voltar_posicao()
            if inimigo.get_hitbox().colliderect(self.player.get_hitbox()):
                inimigo.voltar_posicao()

    # colisão entre o inimigo e o mapa, porém atualmente a IA de seguir o personagem não prevê esse tipo de coisa,
    # então o inimigo fica agarrado. Descomentar no checar_colisoes quando descomentar aqui
    # def _colisao_inimgos_mapa(self):
    #     for collider in self.mapa.colliders:
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
