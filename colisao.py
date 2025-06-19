from pygame import *
import sys
from pygame.locals import QUIT
import math

class Colisao:
    def __init__(self, mapa, player, inimigos):
        self.mapa = mapa
        self.player = player
        self.inimigos = inimigos

    def checar_colisoes(self, player, inimigos, teclas, dt):
        self._colisao_player_mapa(teclas, dt)
        #self._colisao_player_inimigos()
        self._colisao_inimigos_inimigos()
        # self._colisao_inimgos_mapa()

    def checar_mask_collision(self, r1, m1, r2, m2):
        if not r1.colliderect(r2):
            return False
        offset = (r2.x - r1.x, r2.y - r1.y)
        return m1.overlap(m2, offset)

    def _colisao_player_mapa(self, keys, dt):
        speed = self.player.velocidadeMov * dt
        #speed vira aceleração, e vx/vy vira a velocidade mesmo. sem atrito, a velocidade nunca vai ser zerada
        if keys[K_a]: self.player.vx -= speed
        if keys[K_d]: self.player.vx += speed
        if keys[K_w]: self.player.vy -= speed
        if keys[K_s]: self.player.vy += speed

        #diminui a velocidade baseada no atrito. atrito 1 faz com q a velocidade nunca zere, atrito 0 impede o movimento
        self.player.vx *= self.player.atrito
        self.player.vy *= self.player.atrito

        max_vel = self.player.velocidadeMov*10
        self.player.vx = max(-max_vel, min(self.player.vx, max_vel))
        self.player.vy = max(-max_vel, min(self.player.vy, max_vel))

        if self.player.is_dashing:
            dash_speed = self.player.velocidadeMov * dt * 2.5
            direcao = self.player.dash_direcao
            if direcao == 'a': self.player.vx = -dash_speed
            elif direcao == 'd': self.player.vx = dash_speed
            elif direcao == 'w': self.player.vy = -dash_speed
            elif direcao == 's': self.player.vy = dash_speed

            self.player.dash_duration += dt
            if self.player.dash_duration >= self.player.dash_duration_max:
                self.player.is_dashing = False

        new_rect = self.player.player_rect.copy()
        area_interesse = Rect(new_rect.x - 100, new_rect.y - 100, new_rect.width + 200, new_rect.height + 200)

        can_move_x, can_move_y = True, True
        new_rect.x += self.player.vx
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_x = False
                break

        new_rect.x = self.player.player_rect.x #reseta x
        new_rect.y += self.player.vy
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                # if self.checar_mask_collision(new_rect, self.player.player_mask, collider['rect'], collider['mask']):
                can_move_y = False
                break

        #zera a velocidade se coldiir
        if not can_move_x:
            self.player.vx = 0
        if not can_move_y:
            self.player.vy = 0

        self.player.mover(can_move_x, can_move_y, self.player.vx, self.player.vy)

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
