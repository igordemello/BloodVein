from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo
from utils import resource_path 
from pygame.locals import USEREVENT
from random import randint

class Cerbero(Inimigo):
    def __init__(self, x, y, largura=448, altura=336, hp=5000, velocidade=3, dano=40):
        self.hitbox_offset_x = largura * 0.2
        self.hitbox_offset_y = altura * 0.3
        self.hitbox_largura = largura * 0.6
        self.hitbox_altura = altura * 0.5

        super().__init__(x, y, largura, altura, hp, velocidade, dano)

        self.lava_sprite = transform.scale(
            image.load(resource_path('./assets/Enemies/lava.png')).convert_alpha(),
            (120, 120)
        )

        self.vivo = True
        self.hp = hp
        self.hp_max = hp
        self.tipo_colisao = "obstaculo"
        self.estado = "perseguindo"

        self.projeteis = []
        self.ultimo_ataque = 0
        self.cooldown_ataque = 1500
        self.trail_projetil_max = 5
        self.trail_projetil_fade = 25
        self.dano_bola_fogo = 20
        self.velocidade_projetil = 5
        self.angulo_ajuste = 0.05

        self.animacoes = {
            "idle": self.carregar_animacao(resource_path('./assets/Enemies/atena_andar.png'), 8),
            "patada": self.carregar_animacao(resource_path('./assets/Enemies/atena_ataque.png'), 8),
            "grito": self.carregar_animacao(resource_path('./assets/Enemies/atena_grito.png'), 9),
            "cospe_fogo": self.carregar_animacao(resource_path('./assets/Enemies/atena_fogo.png'), 9),
            "andando": self.carregar_animacao(resource_path('./assets/Enemies/atena_andar.png'), 8),
        }

        self.animacao_atual = "idle"
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.1

        self.cooldown_ataques = {
            "patada": 5000,
            "grito": 8000,
            "cospe_fogo": 10000
        }
        self.tempo_ultimo_ataque = {
            "patada": 0,
            "grito": 0,
            "cospe_fogo": 0
        }

        self.distancia_ataque_patada = 150
        self.contador_patadas = 0
        self.contador_cuspe = 0

        self.lava_posicoes = []
        self.tamanho_lava = (120, 120)
        self.duracao_lava = 5000

        self.hitbox_patada = {
            "esquerda": Rect(0, 0, 80, self.altura),
            "direita": Rect(0, 0, 80, self.altura),
            "baixo": Rect(0, 0, self.largura, 80)
        }

        self.player = None
        self.ultimo_dano = 0
        self.cooldown_dano = 500

    def mover_se(self, pode_x, pode_y, vx, vy):
        if pode_x:
            self.x += vx
        if pode_y:
            self.y += vy
        self.rect.topleft = (round(self.x), round(self.y))

    def set_velocidade_x(self, valor):
        self.vx = valor

    def set_velocidade_y(self, valor):
        self.vy = valor

    def get_velocidade(self):
        return self.vx, self.vy

    def carregar_animacao(self, caminho, total_frames):
        spritesheet = image.load(caminho).convert_alpha()
        frame_width = spritesheet.get_width() // total_frames
        frame_height = spritesheet.get_height()
        frames = []
        for i in range(total_frames):
            frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = transform.scale(frame, (self.largura, self.altura))
            frames.append(frame)
        return frames

    def get_hitbox(self):
        return Rect(
            int(self.x + self.hitbox_offset_x),
            int(self.y + self.hitbox_offset_y),
            int(self.hitbox_largura),
            int(self.hitbox_altura)
        )

    def trocar_estado(self, novo_estado):
        if self.estado != novo_estado:
            self.estado = novo_estado
            self.frame_index = 0
            self.frame_time = 0
            if novo_estado == "patada":
                self.contador_patadas = 0
            elif novo_estado == "cospe_fogo":
                self.contador_cuspe = 0

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animacoes[self.animacao_atual])

    def atualizar(self, player_pos, tela, mapa_matriz, offset):
        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            return

        now = time.get_ticks()

        self.atualizar_animacao()
        self.atualizar_projeteis(player_pos)

        if self.player:
            player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
            if self.verificar_colisao_jogador(player_rect):
                self.player.tomar_dano(self.dano)

        if self.estado == "perseguindo":
            self.executar_perseguir(player_pos, now)
        elif self.estado == "patada":
            self.executar_patada(player_pos, now)
        elif self.estado == "grito":
            self.executar_grito(now, player_pos)
        elif self.estado == "cospe_fogo":
            self.executar_cuspe_fogo(now, player_pos)

    def executar_perseguir(self, player_pos, now):
        dx = player_pos[0] - (self.x + self.largura / 2)
        dy = player_pos[1] - (self.y + self.altura / 2)
        distancia = math.hypot(dx, dy)

        if distancia < self.distancia_ataque_patada and now - self.tempo_ultimo_ataque["patada"] > self.cooldown_ataques["patada"]:
            self.trocar_estado("patada")
            self.tempo_ultimo_ataque["patada"] = now
        elif distancia < 300 and now - self.tempo_ultimo_ataque["grito"] > self.cooldown_ataques["grito"]:
            self.trocar_estado("grito")
            self.tempo_ultimo_ataque["grito"] = now
        elif now - self.tempo_ultimo_ataque["cospe_fogo"] > self.cooldown_ataques["cospe_fogo"]:
            self.trocar_estado("cospe_fogo")
            self.tempo_ultimo_ataque["cospe_fogo"] = now
        else:
            if distancia > 0:
                step = min(self.velocidade, distancia)
                self.vx = step * dx / distancia
                self.vy = step * dy / distancia
                self.set_velocidade_x(self.vx)
                self.set_velocidade_y(self.vy)
                self.animacao_atual = "andando"
            else:
                self.animacao_atual = "idle"

    def executar_patada(self, player_pos, now):
        self.animacao_atual = "patada"
        if self.frame_index == 3 and not hasattr(self, 'patada_atingiu'):
            self.hitbox_patada["esquerda"].topleft = (self.x - 80, self.y)
            self.hitbox_patada["direita"].topleft = (self.x + self.largura, self.y)
            self.hitbox_patada["baixo"].topleft = (self.x, self.y + self.altura)

            player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
            for hitbox in self.hitbox_patada.values():
                if player_rect.colliderect(hitbox) and self.player:
                    self.player.mp = 0
                    self.player.tomar_dano(self.dano)
                    event.post(event.Event(USEREVENT + 10, {}))
            self.patada_atingiu = True

        if self.frame_index >= len(self.animacoes["patada"]) - 1:
            self.trocar_estado("perseguindo")
            if hasattr(self, 'patada_atingiu'):
                del self.patada_atingiu

    def executar_grito(self, now, player_pos):
        self.animacao_atual = "grito"
        if self.frame_index == 4 and not hasattr(self, 'grito_aplicado'):
            if self.player and not hasattr(self.player, 'velocidade_original_grito'):
                self.player.velocidade_original_grito = self.player.velocidadeMov
                self.player.velocidadeMov *= 0.4
                self.player.travado = True
                time.set_timer(USEREVENT + 11, 1000, True)
                time.set_timer(USEREVENT + 12, 5000, True)
            self.grito_aplicado = True

        if self.frame_index >= len(self.animacoes["grito"]) - 1:
            self.trocar_estado("perseguindo")
            if hasattr(self, 'grito_aplicado'):
                del self.grito_aplicado

    def executar_cuspe_fogo(self, now, player_pos):
        self.animacao_atual = "cospe_fogo"
        if self.frame_index in [2, 3, 4] and self.contador_cuspe < 3:
            self.atirar_projetil(player_pos)
            self.contador_cuspe += 1

        if self.frame_index >= len(self.animacoes["cospe_fogo"]) - 1:
            self.contador_cuspe = 0
            self.trocar_estado("perseguindo")

    def atirar_projetil(self, player_pos):
        if time.get_ticks() - self.ultimo_ataque < self.cooldown_ataque:
            return

        px, py = player_pos[0] + 32, player_pos[1] + 32
        angle = math.atan2(py - (self.y + self.altura / 2), px - (self.x + self.largura / 2))

        for i in range(6):
            offset = 15 * (i - 1)
            speed_var = random.uniform(1.8, 2.2)
            self.projeteis.append({
                "x": self.x + self.largura / 2 + offset,
                "y": self.y + self.altura / 2 + offset,
                "vx": math.cos(angle) * self.velocidade_projetil * speed_var,
                "vy": math.sin(angle) * self.velocidade_projetil * speed_var,
                "dano": self.dano_bola_fogo,
                "lifetime": 2000,
                "raio_hitbox": 15,
                "cor": (255, 100 + randint(0, 50), randint(0, 50)),
                "tamanho": 30,
                "trail": [],
                "alvo_x": px,
                "alvo_y": py
            })

        self.ultimo_ataque = time.get_ticks()

    def atualizar_projeteis(self, player_pos=None):
        now = time.get_ticks()
        for p in self.projeteis[:]:
            if player_pos and p["lifetime"] > 500:
                tx, ty = player_pos[0] + 32, player_pos[1] + 32
                dx, dy = tx - p["x"], ty - p["y"]
                ta = math.atan2(dy, dx)
                ca = math.atan2(p["vy"], p["vx"])
                diff = (ta - ca + math.pi) % (2 * math.pi) - math.pi
                na = ca + min(max(diff, -self.angulo_ajuste), self.angulo_ajuste)
                speed = math.hypot(p["vx"], p["vy"])
                p["vx"] = math.cos(na) * speed
                p["vy"] = math.sin(na) * speed

            if len(p["trail"]) < self.trail_projetil_max or random.random() < 0.4:
                p["trail"].append({
                    "x": p["x"],
                    "y": p["y"],
                    "alpha": randint(150, 200),
                    "cor": (255, 50 + randint(0, 50), randint(0, 50)),
                    "tamanho": randint(8, 12),
                    "lifetime": randint(200, 255)
                })

            for part in p["trail"][:]:
                part["alpha"] -= self.trail_projetil_fade
                part["lifetime"] -= self.trail_projetil_fade
                if part["alpha"] <= 0 or part["lifetime"] <= 0:
                    p["trail"].remove(part)

            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["lifetime"] -= 16

            if p["lifetime"] <= 0:
                self.projeteis.remove(p)


    def verificar_colisao(self, dx, dy, mapa_matriz):
        nova_hitbox = self.player_rect.move(dx, dy)
        # checa se a nova hitbox bate em tiles sólidos do mapa
        for linha in mapa_matriz:
            for tile in linha:
                if tile.tipo == "parede" and nova_hitbox.colliderect(tile.rect):
                    return False, False
        return True, True

    def verificar_colisao_jogador(self, player_rect):
        if not self.vivo:
            return False

        now = time.get_ticks()
        hitbox = self.get_hitbox()
        if hitbox.colliderect(player_rect):
            self.ultimo_dano = now

            # Aplica pushback simples no jogador para fora do boss
            dx = player_rect.centerx - hitbox.centerx
            dy = player_rect.centery - hitbox.centery
            distancia = math.hypot(dx, dy)

            if distancia != 0:
                forca_empurrao = 5  # você pode ajustar
                dx_normalizado = dx / distancia
                dy_normalizado = dy / distancia
                self.player.player_rect.x += int(dx_normalizado * forca_empurrao)
                self.player.player_rect.y += int(dy_normalizado * forca_empurrao)
                self.player.x, self.player.y = self.player.player_rect.topleft

            return True
        return False


    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo:
            return
        frame = self.animacoes[self.animacao_atual][self.frame_index]
        if self.anima_hit:
            frame = self.aplicar_efeito_hit(frame)
        tela.blit(frame, (self.x + offset[0], self.y + offset[1]))

        for p in self.projeteis:
            for part in p["trail"]:
                s = Surface((part["tamanho"], part["tamanho"]), SRCALPHA)
                draw.circle(s, part["cor"], (part["tamanho"] // 2, part["tamanho"] // 2), part["tamanho"] // 2)
                s.set_alpha(part["alpha"])
                tela.blit(s, (part["x"] - part["tamanho"] // 2 + offset[0],
                              part["y"] - part["tamanho"] // 2 + offset[1]))

            s = Surface((p["tamanho"], p["tamanho"]), SRCALPHA)
            draw.circle(s, p["cor"], (p["tamanho"] // 2, p["tamanho"] // 2), p["tamanho"] // 2)
            tela.blit(s, (p["x"] - p["tamanho"] // 2 + offset[0],
                          p["y"] - p["tamanho"] // 2 + offset[1]))

        for lava in self.lava_posicoes:
            tela.blit(self.lava_sprite, (lava['rect'].x + offset[0], lava['rect'].y + offset[1]))

        self.desenhar_barra_boss(tela, tela.get_width())

        debug_hitbox = self.get_hitbox()
        debug_hitbox.x += offset[0]
        debug_hitbox.y += offset[1]
        draw.rect(tela, (255, 0, 0, 100), debug_hitbox, 2)

    def desenhar_barra_boss(self, tela, largura_tela):
        if not self.vivo:
            return
        largura_barra = 600
        altura_barra = 20
        x = (largura_tela - largura_barra) // 2
        y = 225
        porcentagem = max(0, min(self.hp / self.hp_max, 1))
        largura_hp = int(porcentagem * largura_barra)
        draw.rect(tela, (50, 50, 50), (x, y, largura_barra, altura_barra))
        draw.rect(tela, (180, 0, 0), (x, y, largura_hp, altura_barra))
        draw.rect(tela, (255, 200, 0), (x, y, largura_barra, altura_barra), 2)

    def definir_jogador(self, player):
        self.player = player
