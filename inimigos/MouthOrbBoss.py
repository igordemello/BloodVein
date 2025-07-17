from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo
from inimigos.orb import Orb

class MouthOrb(Inimigo):
    def __init__(self, x, y, largura=192, altura=192, hp=3000, velocidade=3, dano=40):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.hp = hp
        self.hp_max = hp

        self.tipo_colisao = "voador"
        self.estado = "idle"

        # Spritesheets
        self.animacoes = {
            "idle": self.carregar_animacao("./assets/Enemies/MouthOrb-IdleSheet-Sheet2.png", 12),
            "ataque": self.carregar_animacao("./assets/Enemies/MouthOrb-AttackSheet.png", 4),
            "invocacao": self.carregar_animacao("./assets/Enemies/MouthOrb-SpawnSheet.png", 10),
        }

        self.animacao_atual = "idle"
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.08

        # Controle de ataque
        self.distancia_ataque = 100
        self.cooldown_ataque = 2000
        self.tempo_ultimo_ataque = 0
        self.executando_ataque = False

        # Controle de invocação
        self.cooldown_invocacao = 6000
        self.tempo_ultima_invocacao = 0
        self.invocando = False
        self.orbs_instanciados = []
        self.max_orbs = 3

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)

    def carregar_animacao(self, caminho, total_frames):
        spritesheet = image.load(caminho).convert_alpha()
        frames = []
        for i in range(total_frames):
            rect = Rect(i * 64, 0, 64, 64)
            frame = Surface((64, 64), SRCALPHA)
            frame.blit(spritesheet, (0, 0), rect)
            frame = transform.scale(frame, (self.largura, self.altura))
            frames.append(frame)
        return frames

    def trocar_estado(self, novo_estado):
        if self.estado != novo_estado:
            self.estado = novo_estado
            self.frame_index = 0
            self.frame_time = 0

    def atualizar(self, player_pos, tela, grupo_inimigos=None, colliders=None, dt=None):
        if not self.vivo:
            return

        now = time.get_ticks()

        # Knockback
        if now - self.knockback_time < self.knockback_duration:
            self.x += self.vx
            self.y += self.vy
            self.rect.topleft = (self.x, self.y)
            return
        else:
            self.knockback_x = 0
            self.knockback_y = 0
            self.set_velocidade_x(0)
            self.set_velocidade_y(0)

        # Morte
        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            return

        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distancia = math.hypot(dx, dy)

        # Atacar se estiver perto
        if distancia < self.distancia_ataque and now - self.tempo_ultimo_ataque > self.cooldown_ataque:
            self.trocar_estado("ataque")
            self.tempo_ultimo_ataque = now
            self.executando_ataque = True
            self.vx = self.vy = 0
        # Invocar se cooldown
        elif now - self.tempo_ultima_invocacao > self.cooldown_invocacao and len(self.orbs_instanciados) < self.max_orbs:
            self.trocar_estado("invocacao")
            self.tempo_ultima_invocacao = now
            self.invocando = True
            self.vx = self.vy = 0
        else:
            if self.estado not in ["ataque", "invocacao"]:
                # Movimento simples de perseguição
                self.vx = self.velocidade * dx / distancia if distancia > 1 else 0
                self.vy = self.velocidade * dy / distancia if distancia > 1 else 0
                self.x += self.vx
                self.y += self.vy
                self.trocar_estado("idle")

        self.rect.topleft = (round(self.x), round(self.y))

        # Finalizar ataque/invocação após animação
        if self.estado == "ataque" and self.frame_index == len(self.animacoes["ataque"]) - 1:
            self.executando_ataque = False
            if self.colide_com_player(player_pos):
                if hasattr(self, "dar_dano") and callable(self.dar_dano):
                    self.dar_dano()
            self.trocar_estado("idle")

        if self.estado == "invocacao" and self.frame_index == len(self.animacoes["invocacao"]) - 1:
            self.instanciar_orb(grupo_inimigos or [], colliders or [])
            self.invocando = False
            self.trocar_estado("idle")

        self.atualizar_animacao()
        self.orbs_instanciados = [orb for orb in self.orbs_instanciados if orb.vivo]

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animacoes[self.estado])

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo:
            return


        draw_x = round(self.x + offset[0])
        draw_y = round(self.y + offset[1])
        #HIT VERMELHO COLOCAR ISSO EM TODOS OS INIMIGOS NO METODO DESENHAR DE CADA UM
        if self.anima_hit:
            frame = self.aplicar_efeito_hit(self.animacoes[self.estado][self.frame_index])
        else:
            frame = self.animacoes[self.estado][self.frame_index]
        tela.blit(frame, (draw_x, draw_y))

        self.desenhar_barra_boss(tela, tela.get_width())

    def colide_com_player(self, player_pos):
        player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
        hitbox, _ = self.get_hitbox_ataque(player_pos)
        return hitbox.colliderect(player_rect)

    def instanciar_orb(self, grupo, colliders):
        altura_tela = display.get_surface().get_height()  # Pega a altura da tela atual
        orb_x = self.x + self.largura // 2 - 32

        if self.y < altura_tela // 2:
            # Está na metade superior da tela → orb desce
            orb_y = self.y + self.altura + 10
        else:
            # Está na metade inferior da tela → orb sobe
            orb_y = self.y - 64 - 10

        orb = Orb(orb_x, orb_y, 64, 64)
        grupo.append(orb)
        self.orbs_instanciados.append(orb)

    def get_hitbox_ataque(self, player_pos):
        dx = (player_pos[0] + 32) - (self.x + 32)
        dy = (player_pos[1] + 32) - (self.y + 32)
        angulo = math.atan2(dy, dx)
        orb_x = self.x + 32 + math.cos(angulo) * (self.radius + 15)
        orb_y = self.y + 32 + math.sin(angulo) * (self.radius + 15)
        orb_rect = Rect(0, 0, *self.orbital_size)
        orb_rect.center = (orb_x, orb_y)
        orb_surf = Surface(self.hitbox_arma, SRCALPHA)
        rot_surf = transform.rotate(orb_surf, -math.degrees(angulo))
        rot_rect = rot_surf.get_rect(center=orb_rect.center)
        return rot_rect, rot_surf

    def desenhar_barra_boss(self, tela, largura_tela):
        if not self.vivo:
            return

        tempo_apos_dano = time.get_ticks() - self.ultimo_dano_tempo
        if tempo_apos_dano > 4000:
            return  # só exibe a barra por 4 segundos após o dano

        # Configurações da barra
        largura_barra = 600
        altura_barra = 20
        x = (largura_tela - largura_barra) // 2
        y = 225  # margem do topo

        vida_maxima = getattr(self, "hp_max", self.hp)
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = int(porcentagem * largura_barra)

        # Fundo
        draw.rect(tela, (50, 50, 50), (x, y, largura_barra, altura_barra))
        # Vida
        draw.rect(tela, (180, 0, 0), (x, y, largura_hp, altura_barra))
        # Moldura
        draw.rect(tela, (255, 200, 0), (x, y, largura_barra, altura_barra), 2)
