from pygame import *
import sys
from pygame.locals import QUIT
import math

class Colisao:
    def __init__(self, mapa, player):
        self.player = player
        self.mapa = mapa
        self.entidades = []  

    def adicionar_entidade(self, entidade):
        self.entidades.append(entidade)

    def remover_entidades_menos_player(self):
        from player import Player
        self.entidades = [ent for ent in self.entidades if isinstance(ent, Player)]

    def checar_colisoes(self,dt):

        for i, ent1 in enumerate(self.entidades):
            for ent2 in self.entidades[i+1:]:
                self._colisao_entidade_entidade(ent1, ent2)

        for entidade in self.entidades:
            self._colisao_entidade_mapa(entidade, dt)


    def _colisao_entidade_mapa(self,entidade,dt):
        vx, vy = entidade.get_velocidade()
        new_rect = entidade.get_hitbox().copy()
        

        area_interesse = Rect(
            new_rect.x - 100, new_rect.y - 100,
            new_rect.width + 200, new_rect.height + 200
        )
        

        can_move_x, can_move_y = True, True
        

        new_rect.x += vx
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                can_move_x = False
                break
        

        new_rect.x = entidade.get_hitbox().x
        new_rect.y += vy
        for collider in self.mapa.colliders:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                can_move_y = False
                break
        

        entidade.mover_se(can_move_x, can_move_y, vx, vy)


        if not can_move_x:
            entidade.set_velocidade_x(0)
        if not can_move_y:
            entidade.set_velocidade_y(0)


    def _colisao_entidade_entidade(self, ent1, ent2):
        if self.player.is_dashing:
            return
        vx1, vy1 = ent1.get_velocidade()
        vx2, vy2 = ent2.get_velocidade()

        can_move_x1, can_move_y1 = True, True
        can_move_x2, can_move_y2 = True, True

        # Movimento no eixo X
        rect1_x = ent1.get_hitbox().copy()
        rect2_x = ent2.get_hitbox().copy()
        rect1_x.x += vx1
        rect2_x.x += vx2

        if rect1_x.colliderect(rect2_x) and ent1.hp>0 and ent2.hp > 0:
            can_move_x1 = False
            can_move_x2 = False

        # Movimento no eixo Y
        rect1_y = ent1.get_hitbox().copy()
        rect2_y = ent2.get_hitbox().copy()
        rect1_y.y += vy1
        rect2_y.y += vy2

        if rect1_y.colliderect(rect2_y) and ent1.hp>0 and ent2.hp > 0:
            can_move_y1 = False
            can_move_y2 = False

        # Aplica o movimento parcial (igual ao mapa)
        ent1.set_velocidade_x(vx1 if can_move_x1 else 0)
        ent1.set_velocidade_y(vy1 if can_move_y1 else 0)

        ent2.set_velocidade_x(vx2 if can_move_x2 else 0)
        ent2.set_velocidade_y(vy2 if can_move_y2 else 0)