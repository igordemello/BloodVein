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

        self._colisao_entidade_projetil()
        self._colisao_entidade_AOE()


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

    def _colisao_entidade_projetil(self):
        from player import Player
        for projetil in self.player.projeteis[:]:
            projetil_rect = Rect(
                projetil["x"] - projetil["raio_hitbox"],
                projetil["y"] - projetil["raio_hitbox"],
                projetil["raio_hitbox"] * 2,
                projetil["raio_hitbox"] * 2
            )
            for inimigo in self.entidades:
                if isinstance(inimigo, Player):
                    pass
                elif inimigo.vivo and projetil_rect.colliderect(inimigo.get_hitbox()):
                    current_time = time.get_ticks()
                    if current_time - self.player.tempo_ultimo_hit_projetil > self.player.tempo_max_combo:
                        self.player.hits_projetil = 0
                        self.player.arma.comboMult = 1.0
                    self.player.hits_projetil += 1
                    self.player.tempo_ultimo_hit_projetil = current_time
                    self.player.arma.comboMult = 1.0 + (0.1 * self.player.hits_projetil)

                    inimigo.hp -= projetil["dano"] * self.player.arma.comboMult
                    inimigo.ultimo_dano_critico = False
                    inimigo.ultimo_dano = projetil["dano"] * self.player.arma.comboMult
                    inimigo.ultimo_dano_tempo = time.get_ticks()

                    dx = inimigo.x - self.player.x
                    dy = inimigo.y - self.player.y
                    inimigo.aplicar_knockback(dx, dy, intensidade=1)

                    self.player.criar_efeito_sangue(projetil["x"], projetil["y"])

                    self.player.projeteis.remove(projetil)
                    if self.player.arma.ataqueTipo == "ranged" and self.player.hp < 100:
                        self.player.hp += self.player.arma.lifeSteal
                        if self.player.hp > 100:
                            self.player.hp = 100
                    break

    def _colisao_entidade_AOE(self):
        from player import Player

        tempo_atual = time.get_ticks()

        if not hasattr(self, "ultimo_tempo_colisao_aoe"):
            self.ultimo_tempo_colisao_aoe = 0

        if self.player.aoe is not None and tempo_atual - self.ultimo_tempo_colisao_aoe >= 1000:
            for inimigo in self.entidades:
                if isinstance(inimigo, Player):
                    continue
                if inimigo.vivo and self.player.aoe[1].colliderect(inimigo.get_hitbox()):
                    inimigo.hp -= self.player.arma.danoAOE
                    inimigo.ultimo_dano_critico = False
                    inimigo.ultimo_dano = self.player.arma.danoAOE
                    inimigo.ultimo_dano_tempo = tempo_atual

                    self.ultimo_tempo_colisao_aoe = tempo_atual
                    break