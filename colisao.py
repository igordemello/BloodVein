from pygame import *
import sys
from pygame.locals import QUIT
import math


class Colisao:
    def __init__(self, mapa):
        self.mapa = mapa
        self.entidades = []  

    def adicionar_entidade(self, entidade):
        self.entidades.append(entidade)

    def remover_entidades_menos_player(self):
        from player import Player
        self.entidades = [ent for ent in self.entidades if isinstance(ent, Player)]

    def checar_colisoes(self,dt):
        for entidade in self.entidades:
            self._colisao_entidade_mapa(entidade, dt)

        # for i, ent1 in enumerate(self.entidades):
        #     for ent2 in self.entidades[i+1:]:
        #         self._colisao_entidade_entidade(ent1, ent2)

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