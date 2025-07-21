from pygame import *
import sys
from pygame.locals import QUIT
import math

from utils import resource_path 
from screen_shake import screen_shaker


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

    def checar_colisoes(self, dt):
        from player import Player
        from inimigos.orb import Orb
        from inimigos.zombie import Zombie
        from inimigos.aranha_lunar import AranhaLunar
        from inimigos.esqueleto_gelo import EsqueletoGelo
        from inimigos.esqueleto_peconhento import EsqueletoPeconhento
        from inimigos.Cachorro import Cerbero

        for i, ent1 in enumerate(self.entidades):
            # Ignora completamente o Orb (não colide com ninguém)
            if isinstance(ent1, Orb):
                continue

            for ent2 in self.entidades[i + 1:]:
                if isinstance(ent2, Orb):
                    continue

                # Ignora Player com qualquer coisa que não seja Zombie ou AranhaLunar
                if isinstance(ent1, Player):
                    if not isinstance(ent2, (Zombie, AranhaLunar, EsqueletoGelo, EsqueletoPeconhento,Cerbero)):
                        continue
                elif isinstance(ent2, Player):
                    if not isinstance(ent1, (Zombie, AranhaLunar, EsqueletoGelo, EsqueletoPeconhento,Cerbero)):
                        continue

                # Ignora colisões entre zombies
                if isinstance(ent1, Zombie) and isinstance(ent2, Zombie):
                    continue

                # Ignora colisões entre aranhas
                if isinstance(ent1, AranhaLunar) and isinstance(ent2, AranhaLunar):
                    continue

                if isinstance(ent1, EsqueletoGelo) and isinstance(ent2, EsqueletoGelo):
                    continue

                if isinstance(ent1, EsqueletoPeconhento) and isinstance(ent2, EsqueletoPeconhento):
                    continue

                self._colisao_entidade_entidade(ent1, ent2)

        for entidade in self.entidades:
            if entidade.tipo_colisao == 'voador':
                self._colisao_entidade_mapa_sem_obstaculo(entidade)
            elif entidade.tipo_colisao == 'obstaculo':
                self._colisao_entidade_mapa_contando_obstaculo(entidade)


        #self._colisao_entidade_mapa_contando_obstaculo(self.player)
        self._colisao_entidade_projetil()
        self._colisao_entidade_AOE()
        self._colisao_entidade_AOE_uma_vez()
        self._colisao_projetil_mapa()
        self._colisao_projetil_inimigo_player()


    def _colisao_entidade_mapa_contando_obstaculo(self,entidade):
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


    def _colisao_entidade_mapa_sem_obstaculo(self,entidade):
        vx, vy = entidade.get_velocidade()
        new_rect = entidade.get_hitbox().copy()


        area_interesse = Rect(
            new_rect.x - 100, new_rect.y - 100,
            new_rect.width + 200, new_rect.height + 200
        )


        can_move_x, can_move_y = True, True


        new_rect.x += vx
        for collider in self.mapa.colliders_sem_obstaculo:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                can_move_x = False
                break


        new_rect.x = entidade.get_hitbox().x
        new_rect.y += vy
        for collider in self.mapa.colliders_sem_obstaculo:
            if area_interesse.colliderect(collider['rect']) and new_rect.colliderect(collider['rect']):
                can_move_y = False
                break


        entidade.mover_se(can_move_x, can_move_y, vx, vy)


        if not can_move_x:
            entidade.set_velocidade_x(0)
        if not can_move_y:
            entidade.set_velocidade_y(0)


    def _colisao_entidade_entidade(self, ent1, ent2):
        # if self.player.is_dashing:
        #     return
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

                    inimigo.tomar_dano(projetil["dano"] * self.player.arma.comboMult)
                    inimigo.ultimo_dano_critico = False
                    inimigo.ultimo_dano = projetil["dano"] * self.player.arma.comboMult
                    inimigo.ultimo_dano_tempo = time.get_ticks()
                    screen_shaker.start(intensity=5, duration=150)

                    dx = inimigo.x - self.player.x
                    dy = inimigo.y - self.player.y
                    inimigo.aplicar_knockback(dx, dy, intensidade=0.8)

                    self.player.criar_efeito_sangue(projetil["x"], projetil["y"])

                    self.player.projeteis.remove(projetil)
                    if self.player.arma.ataqueTipo == "ranged" and self.player.hp < 100:
                        self.player.hp += self.player.arma.lifeSteal
                        if self.player.hp > 100:
                            self.player.hp = 100

                    if self.player.nevascaAtivada:
                        inimigo.velocidade *= 0.5
                        inimigo.congelado = True
                        self.player.nevascaAtivada = False
                    elif self.player.trovaoAtivado:
                        inimigo.stunar(2)
                        self.player.trovaoAtivado = False
                    break

    def _colisao_entidade_AOE(self):
        from player import Player

        tempo_atual = time.get_ticks()

        if not hasattr(self, "ultimo_tempo_colisao_aoe"):
            self.ultimo_tempo_colisao_aoe = 0

        if self.player.aoe is not None and tempo_atual - self.ultimo_tempo_colisao_aoe >= 1000 and not self.player.claraoAtivado:
            for inimigo in self.entidades:
                if isinstance(inimigo, Player):
                    continue
                if inimigo.vivo and self.player.aoe[1].colliderect(inimigo.get_hitbox()):
                    inimigo.tomar_dano(self.player.arma.danoAOE)
                    inimigo.ultimo_dano_critico = False
                    inimigo.ultimo_dano = self.player.arma.danoAOE
                    inimigo.ultimo_dano_tempo = tempo_atual

                    self.ultimo_tempo_colisao_aoe = tempo_atual
                    break
        if self.player.aoeVeneno is not None and tempo_atual - self.ultimo_tempo_colisao_aoe >= 1000 and not self.player.claraoAtivado:
            for inimigo in self.entidades:
                if isinstance(inimigo, Player):
                    continue
                if inimigo.vivo and self.player.aoeVeneno[1].colliderect(inimigo.get_hitbox()):
                    inimigo.tomar_dano(self.player.venenoDano)
                    inimigo.ultimo_dano_critico = False
                    inimigo.ultimo_dano = self.player.venenoDano
                    inimigo.ultimo_dano_tempo = tempo_atual

                    self.ultimo_tempo_colisao_aoe = tempo_atual
                    break

    def _colisao_entidade_AOE_uma_vez(self):
        from player import Player

        if not hasattr(self.player, 'claraoAtivado') or not self.player.claraoAtivado:
            return

        if self.player.aoe is None:
            return

        for inimigo in self.entidades:
            if isinstance(inimigo, Player):
                continue
            if (inimigo.vivo
                    and self.player.aoe[1].colliderect(inimigo.get_hitbox())
                    and inimigo not in self.player.inimigos_atingidos_este_clarao):
                inimigo.tomar_dano(self.player.claraoDano)
                inimigo.ultimo_dano_critico = False
                inimigo.ultimo_dano = self.player.claraoDano
                inimigo.ultimo_dano_tempo = time.get_ticks()

                self.player.inimigos_atingidos_este_clarao.append(inimigo)

    def _colisao_projetil_mapa(self):
        for projetil in self.player.projeteis[:]:
            projetil_rect = Rect(
                projetil["x"] - projetil["raio_hitbox"],
                projetil["y"] - projetil["raio_hitbox"],
                projetil["raio_hitbox"] * 2,
                projetil["raio_hitbox"] * 2
            )

            for collider in self.mapa.colliders_sem_obstaculo:
                if projetil_rect.colliderect(collider['rect']):
                    if projetil in self.player.projeteis:
                        self.player.projeteis.remove(projetil)
                    break

    def _colisao_projetil_inimigo_player(self):
        from player import Player
        for inimigo in self.entidades:
            if hasattr(inimigo, 'projeteis') and not isinstance(inimigo, Player):
                for projetil in inimigo.projeteis[:]:
                    # Criar hitbox circular mais precisa
                    projetil_raio = projetil["raio_hitbox"]
                    centro_projetil = (projetil["x"], projetil["y"])

                    # Verificar colisão com player (também circular)
                    player_rect = self.player.get_hitbox()
                    player_centro = (player_rect.centerx, player_rect.centery)
                    player_raio = max(player_rect.width, player_rect.height) // 2

                    distancia = math.sqrt((centro_projetil[0] - player_centro[0]) ** 2 +
                                          (centro_projetil[1] - player_centro[1]) ** 2)

                    if distancia < (projetil_raio + player_raio):
                        self.player.tomar_dano(projetil["dano"])
                        inimigo.projeteis.remove(projetil)
                        break

                    # Colisão com o mapa SOMENTE PAREDES
                    for collider in self.mapa.colliders_sem_obstaculo:
                        if Rect(projetil["x"] - projetil_raio, projetil["y"] - projetil_raio,
                                projetil_raio * 2, projetil_raio * 2).colliderect(collider['rect']):
                            if projetil in inimigo.projeteis:
                                inimigo.projeteis.remove(projetil)
                            break


