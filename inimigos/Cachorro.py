from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo
from utils import resource_path 
from pygame.locals import USEREVENT
from random import uniform, randint

class Cerbero(Inimigo):
    def __init__(self, x, y, largura=256, altura=256, hp=5000, velocidade=3, dano=40):
        # Initialize hitbox parameters BEFORE calling parent's __init__
        self.hitbox_offset_x = largura * 0.2  # 20% de margem lateral
        self.hitbox_offset_y = altura * 0.3   # 30% de margem superior
        self.hitbox_largura = largura * 0.6   # 60% da largura total
        self.hitbox_altura = altura * 0.5     # 50% da altura total
        
        # Now call parent's __init__
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        
        self.vivo = True
        self.hp = hp
        self.hp_max = hp
        self.tipo_colisao = "terrestre"
        self.estado = "perseguindo"  # Estados: perseguindo, patada, grito, cospe_fogo

        # Sistema de projéteis teleguiados
        self.projeteis = []
        self.ultimo_ataque = 0
        self.cooldown_ataque = 1500
        self.trail_projetil_max = 5
        self.trail_projetil_fade = 25
        self.dano_bola_fogo = 20
        self.velocidade_projetil = 5
        self.angulo_ajuste = 0.05

        # Carregar animações
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

        # Controle de ataques
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
        
        # Lava
        self.lava_posicoes = []
        self.tamanho_lava = (120, 120)
        self.duracao_lava = 5000
        
        # Configurações de hitbox de ataque
        self.hitbox_patada = {
            "esquerda": Rect(0, 0, 80, self.altura),
            "direita": Rect(0, 0, 80, self.altura),
            "baixo": Rect(0, 0, self.largura, 80)
        }
        
        # Referência ao jogador
        self.player = None

    def get_hitbox(self):
        """Retorna a hitbox atualizada na posição correta"""
        return Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_largura,
            self.hitbox_altura
        )


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
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_largura,
            self.hitbox_altura
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

        # Lógica de estados
        if self.estado == "perseguindo":
            self.executar_perseguir(player_pos, now)
        elif self.estado == "patada":
            self.executar_patada(player_pos, now)
        elif self.estado == "grito":
            self.executar_grito(now, player_pos)
        elif self.estado == "cospe_fogo":
            self.executar_cuspe_fogo(now, player_pos)

        self.atualizar_lava(now)
        self.rect.topleft = (self.x, self.y)

    def executar_perseguir(self, player_pos, now):
        dx = player_pos[0] - (self.x + self.largura/2)
        dy = player_pos[1] - (self.y + self.altura/2)
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
                self.vx = self.velocidade * dx / distancia
                self.vy = self.velocidade * dy / distancia
                self.x += self.vx
                self.y += self.vy
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
            
            for direcao, hitbox in self.hitbox_patada.items():
                if player_rect.colliderect(hitbox) and self.player:
                    self.player.tomar_dano(self.dano)
                    event.post(event.Event(USEREVENT+10, {}))  # Evento de desativar habilidades
            
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
                self.player.velocidadeMov = self.player.velocidade_original_grito * 0.4
                self.player.travado = True

                time.set_timer(USEREVENT + 11, 1000, True)   # Libera paralisia após 1s
                time.set_timer(USEREVENT + 12, 5000, True)   # Restaura velocidade após 5s

            self.grito_aplicado = True

        if self.frame_index >= len(self.animacoes["grito"]) - 1:
            self.trocar_estado("perseguindo")
            if hasattr(self, 'grito_aplicado'):
                del self.grito_aplicado

    def executar_cuspe_fogo(self, now, player_pos):
        self.animacao_atual = "cospe_fogo"
        
        if self.frame_index in [2, 3, 4] and self.contador_cuspe < 3:
            self.atirar_projetil(player_pos)
            
            # Cria área de lava
            lava_x = player_pos[0] + random.randint(-150, 150)
            lava_y = player_pos[1] + random.randint(-150, 150)
            self.lava_posicoes.append({
                'rect': Rect(lava_x, lava_y, self.tamanho_lava[0], self.tamanho_lava[1]),
                'criado': now
            })
            
            self.contador_cuspe += 1

        if self.frame_index >= len(self.animacoes["cospe_fogo"]) - 1:
            self.contador_cuspe = 0
            self.trocar_estado("perseguindo")

    def atirar_projetil(self, player_pos):
        """Cria projéteis de fogo teleguiados"""
        now = time.get_ticks()
        if now - self.ultimo_ataque < self.cooldown_ataque:
            return

        player_x = player_pos[0] + 32
        player_y = player_pos[1] + 32
        angle = math.atan2(player_y - (self.y + self.altura / 2),
                           player_x - (self.x + self.largura / 2))

        for i in range(3):  # Cria 3 projéteis
            offset = 15 * (i - 1)  # -15, 0, +15
            speed_variation = random.uniform(0.8, 1.2)
            
            projetil = {
                "x": self.x + self.largura / 2 + offset,
                "y": self.y + self.altura / 2 + offset,
                "vx": math.cos(angle) * self.velocidade_projetil * speed_variation,
                "vy": math.sin(angle) * self.velocidade_projetil * speed_variation,
                "dano": self.dano_bola_fogo,
                "lifetime": 2000,
                "raio_hitbox": 15,
                "cor": (255, 100 + randint(0, 50), randint(0, 50)),
                "tamanho": 20,
                "trail": [],
                "alvo_x": player_x,
                "alvo_y": player_y
            }
            self.projeteis.append(projetil)

        self.ultimo_ataque = now

    def atualizar_projeteis(self, player_pos=None):
        now = time.get_ticks()
        for projetil in self.projeteis[:]:
            # Sistema de teleguia
            if player_pos and projetil["lifetime"] > 500:
                target_x, target_y = player_pos[0] + 32, player_pos[1] + 32
                dx = target_x - projetil["x"]
                dy = target_y - projetil["y"]
                target_angle = math.atan2(dy, dx)
                
                current_angle = math.atan2(projetil["vy"], projetil["vx"])
                angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                new_angle = current_angle + min(max(angle_diff, -self.angulo_ajuste), self.angulo_ajuste)
                
                speed = math.hypot(projetil["vx"], projetil["vy"])
                projetil["vx"] = math.cos(new_angle) * speed
                projetil["vy"] = math.sin(new_angle) * speed

            # Sistema de partículas do rastro
            if len(projetil["trail"]) < self.trail_projetil_max or random.random() < 0.4:
                projetil["trail"].append({
                    "x": projetil["x"],
                    "y": projetil["y"],
                    "alpha": randint(150, 200),
                    "cor": (255, 50 + randint(0, 50), randint(0, 50)),
                    "tamanho": randint(8, 12),
                    "lifetime": randint(200, 255)
                })

            for part in projetil["trail"][:]:
                part["alpha"] = max(0, part["alpha"] - self.trail_projetil_fade)
                if part["alpha"] <= 0:
                    projetil["trail"].remove(part)

            projetil["x"] += projetil["vx"]
            projetil["y"] += projetil["vy"]
            projetil["lifetime"] -= 1

            if projetil["lifetime"] <= 0:
                self.projeteis.remove(projetil)

    def atualizar_lava(self, now):
        for lava in self.lava_posicoes[:]:
            if now - lava['criado'] > self.duracao_lava:
                self.lava_posicoes.remove(lava)

    def verificar_colisao_jogador(self, player_rect):
        """Verifica colisão usando a hitbox dinâmica"""
        if not self.vivo:
            return False
            
        return self.get_hitbox().colliderect(player_rect)

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo:
            return
        
        # Desenha o boss
        frame = self.animacoes[self.animacao_atual][self.frame_index]
        if self.anima_hit:
            frame = self.aplicar_efeito_hit(frame)
        
        tela.blit(frame, (self.x + offset[0], self.y + offset[1]))
        
        # Desenha projéteis
        for projetil in self.projeteis:
            # Rastro
            for part in projetil["trail"]:
                s = Surface((part["tamanho"], part["tamanho"]), SRCALPHA)
                draw.circle(s, part["cor"],
                            (part["tamanho"] // 2, part["tamanho"] // 2),
                            part["tamanho"] // 2)
                s.set_alpha(part["alpha"])
                tela.blit(s, (part["x"] - part["tamanho"] // 2 + offset[0],
                            part["y"] - part["tamanho"] // 2 + offset[1]))

            # Projétil principal
            s = Surface((projetil["tamanho"], projetil["tamanho"]), SRCALPHA)
            draw.circle(s, projetil["cor"],
                        (projetil["tamanho"] // 2, projetil["tamanho"] // 2),
                        projetil["tamanho"] // 2)
            tela.blit(s, (projetil["x"] - projetil["tamanho"] // 2 + offset[0],
                        projetil["y"] - projetil["tamanho"] // 2 + offset[1]))
        
        # Desenha lava
        for lava in self.lava_posicoes:
            s = Surface(self.tamanho_lava, SRCALPHA)
            s.fill((255, 50, 50, 150))
            tela.blit(s, (lava['rect'].x + offset[0], lava['rect'].y + offset[1]))
        
        # Desenha barra de vida
        self.desenhar_barra_boss(tela, tela.get_width())

        # Debug: mostra hitbox (comentar na versão final)
        debug_hitbox = self.get_hitbox()
        debug_hitbox.x += offset[0]
        debug_hitbox.y += offset[1]
        draw.rect(tela, (255, 0, 0, 100), debug_hitbox, 2)

    def desenhar_barra_boss(self, tela, largura_tela):
        if not self.vivo:
            return

        tempo_apos_dano = time.get_ticks() - self.ultimo_dano_tempo
        if tempo_apos_dano > 4000:
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
        """Define a referência ao jogador"""
        self.player = player