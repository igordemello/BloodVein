from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *
import time as t
from sala import *
from armas import *
from random import *
from sistemaparticulas import *


class Player():
    def __init__(self, x, y, largura, altura, hp=100, st=100, velocidadeMov=0.5, sprite='hero.png'):
        # animações
        self.animacoes = {
            "baixo": self.carregar_animacao("assets/Player/vampira_andando_frente.png"),
            "cima": self.carregar_animacao("assets/Player/vampira_andando_tras.png"),
            "D_cima": self.carregar_animacao("assets/Player/dash_frente.png"),
            "D_baixo": self.carregar_animacao("assets/Player/dash_costas.png"),
            "D_direita": self.carregar_animacao("assets/Player/dash _lado.png"),
            "D_esquerda": [transform.flip(img, True, False) for img in
                           self.carregar_animacao("assets/Player/dash _lado.png")],
            "direita": self.carregar_animacao("assets/Player/LADOANDAR-Sheet.png"),
            "esquerda": [transform.flip(img, True, False) for img in
                         self.carregar_animacao("assets/Player/LADOANDAR-Sheet.png")],
        }
        self.anim_direcao = "baixo"
        self.anim_frame = 0
        self.tempo_animacao = 0
        self.tempo_por_frame = 100
        self.frame_atual = self.animacoes[self.anim_direcao][self.anim_frame]
        self.rastros = []

        self.sistemaparticulas = ParticleSystem()
        self.lista_mods = ListaMods()
        #ARMA
        self.arma = EspadaEstelar("comum", self.lista_mods)
        self.arma.aplicaModificador()

        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.ultimo_uso = 0
        self.hp = hp
        self.hpMax = 100
        self.velocidadeMov = velocidadeMov
        self.rate = 1
        self.rateSt = 1
        self.revives = 0
        self.custoDash = 2.75
        self.modificadorDanoRecebido = 1
        self.ultimo_dano = 0
        self.invencibilidade = 1500
        self.foi_atingido = False
        self.tempo_atingido = 0
        self.itens = {}
        self.itemAtivo = None
        self.salaAtivoUsado = None
        self.itemAtivoEsgotado = None
        self.st = st
        self.cooldown_st = 3000
        self.almas = 999
        self.old_x = x
        self.old_y = y
        self.vx = 0
        self.vy = 0
        self.atrito = 0.92
        self.radius = self.arma.radius - 50
        self.orbital_size = (40, 20)
        self.hitbox_arma = self.arma.range
        self.atacou = False
        self.hits = 0
        self.tempo_ultimo_hit = 0
        self.tempo_max_combo = 2500
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_cooldown_max = 1000
        self.dash_duration_max = 150
        self.is_dashing = False
        self.last_dash_time = 0
        self.dash_direcao = None
        self.parado_desde = 0
        self.ativo_ultimo_uso = 0

        # Sistema de ataque modificado
        self.sword = transform.scale(transform.flip(image.load(self.arma.sprite).convert_alpha(), True, True),
                                     (self.arma.size))
        self.sword_pivot = (20, 0)
        self.sword_angle = 0
        self.attacking = False
        self.attack_start_time = 0
        self.attack_direction = 1
        self.attack_progress = 0
        self.base_sword_angle = 0
        self.sword_arc = 210  # Arco aumentado (original 150)
        self.sword_start_angle = -105  # Ângulo inicial ajustado

        self.projeteis = []

        self.cooldown_ataque_base = self.arma.cooldown
        self.ultimo_ataque = 0
        self.sprite_dano = self.frame_atual.copy()
        self.sprite_dano.fill((255, 255, 255), special_flags=BLEND_RGB_ADD)

        clock = time.Clock()
        self.dt = clock.get_time()
        self.player_img = self.frame_atual
        self.player_rect = self.get_hitbox()
        self.dx = 0
        self.dy = 0

        #efeito espada
        self.sword_trail = []
        self.max_trail_length = 5
        self.trail_alpha = 100  # Transparência do rastro

    # [Métodos auxiliares permanecem iguais...]
    def carregar_animacao(self, caminho):
        frame_largura = 32
        frame_altura = 48
        escala = 2.7
        folha = transform.scale(image.load(caminho).convert_alpha(), (
            image.load(caminho).convert_alpha().get_width() * escala,
            image.load(caminho).convert_alpha().get_height() * escala))
        num_frames = int(folha.get_width() // (frame_largura * escala))

        return [
            folha.subsurface((i * frame_largura * escala, 0, frame_largura * escala, frame_altura * escala))
            for i in range(num_frames)
        ]

    def _dash(self, dt, teclas, direcao):
        current_time = time.get_ticks()

        if (current_time - self.last_dash_time > self.dash_cooldown_max and
                not self.is_dashing and teclas[K_SPACE] and self.st >= self.custoDash):
            self.last_dash_time = current_time
            self.is_dashing = True
            self.dash_direcao = direcao
            self.dash_duration = 0

        if self.is_dashing:
            self.st -= self.custoDash
        self.ultimo_uso = current_time

    def usarItemAtivo(self, sala_atual: Sala):
        if isinstance(self.itemAtivo, ItemAtivo):
            if self.itemAtivo.afetaIni:
                self.itemAtivo.listaInimigos = sala_atual.inimigos
            else:
                self.itemAtivo.player = self
            self.itemAtivo.aplicar_em()
            self.itemAtivo.usos -= 1
            self.salaAtivoUsado = sala_atual
            if self.itemAtivo.usos == 0:
                self.itemAtivoEsgotado = self.itemAtivo
                self.itemAtivo = None
        else:
            print("Não tem item ativo")

    def atualizar(self, dt, teclas):
        self.dt = dt
        current_time = time.get_ticks()
        self.old_x = self.x
        self.old_y = self.y
        self.x, self.y = self.player_rect.topleft

        speed = self.velocidadeMov * dt
        move_input = False

        if teclas[K_a]:
            self.vx -= speed
            self.anim_direcao = "esquerda"
            move_input = True
        if teclas[K_d]:
            self.vx += speed
            self.anim_direcao = "direita"
            move_input = True
        if teclas[K_w]:
            self.vy -= speed
            self.anim_direcao = "cima"
            move_input = True
        if teclas[K_s]:
            self.vy += speed
            self.anim_direcao = "baixo"
            move_input = True

        self.vx *= self.atrito
        self.vy *= self.atrito
        max_vel = self.velocidadeMov * 10
        self.vx = max(-max_vel, min(self.vx, max_vel))
        self.vy = max(-max_vel, min(self.vy, max_vel))

        if teclas[K_d]:
            self._dash(dt, teclas, 'd')
        elif teclas[K_a]:
            self._dash(dt, teclas, 'a')
        elif teclas[K_w]:
            self._dash(dt, teclas, 'w')
        elif teclas[K_s]:
            self._dash(dt, teclas, 's')

        if self.is_dashing:
            self.rastros.append({
                "imagem": self.frame_atual.copy(),
                "pos": self.player_rect.topleft,
                "tempo": 200
            })

            dash_speed = self.velocidadeMov * dt * 2.5
            direcao = self.dash_direcao
            if direcao == 'a':
                self.vx = -dash_speed
                self.anim_direcao = "D_esquerda"
            elif direcao == 'd':
                self.vx = dash_speed
                self.anim_direcao = "D_direita"
            elif direcao == 'w':
                self.vy = -dash_speed
                self.anim_direcao = "D_cima"
            elif direcao == 's':
                self.vy = dash_speed
                self.anim_direcao = "D_baixo"

            self.dash_duration += dt
            if self.dash_duration >= self.dash_duration_max:
                self.is_dashing = False
                self.anim_frame = 0

                if self.dash_direcao == 'a':
                    self.anim_direcao = 'esquerda'
                elif self.dash_direcao == 'd':
                    self.anim_direcao = 'direita'
                elif self.dash_direcao == 'w':
                    self.anim_direcao = 'cima'
                elif self.dash_direcao == 's':
                    self.anim_direcao = 'baixo'

        for rastro in self.rastros:
            rastro["tempo"] -= dt
        self.rastros = [r for r in self.rastros if r["tempo"] > 0]

        if self.is_dashing or move_input:
            self.tempo_animacao += dt
            if self.tempo_animacao > self.tempo_por_frame:
                self.tempo_animacao = 0
                self.anim_frame = (self.anim_frame + 1) % len(self.animacoes[self.anim_direcao])
        else:
            self.anim_frame = 0
            angulo = self.calcular_angulo(mouse.get_pos())
            angulo_deg = math.degrees(angulo) % 360

            if 45 < angulo_deg <= 135:
                self.anim_direcao = "baixo"
            elif 135 < angulo_deg <= 225:
                self.anim_direcao = "esquerda"
            elif 225 < angulo_deg <= 315:
                self.anim_direcao = "cima"
            else:
                self.anim_direcao = "direita"

        self.hp -= 0.05 * self.rate

        if current_time - self.last_dash_time >= self.cooldown_st:
            self.st += 0.7 * self.rateSt

        if self.hp < 0:
            self.hp = 0
        if self.st < 0:
            self.st = 0
        if self.st > 100:
            self.st = 100

        if self.attacking:
            self.atualizar_ataque(dt)

        if self.anim_direcao in self.animacoes:
            animacao = self.animacoes[self.anim_direcao]
            self.anim_frame %= len(animacao)
            self.frame_atual = animacao[self.anim_frame]
        else:
            self.frame_atual = self.animacoes["baixo"][0]

        self.player_rect = self.get_hitbox()
        self.sistemaparticulas.update(dt)

        if self.hits > 0 and time.get_ticks() - self.tempo_ultimo_hit > self.tempo_max_combo:
            self.hits = 0
            self.arma.comboMult = 1

        for projetil in self.projeteis[:]:
            projetil["x"] += projetil["vx"] * dt
            projetil["y"] += projetil["vy"] * dt
            projetil["lifetime"] -= dt
            if projetil["lifetime"] <= 0:
                self.projeteis.remove(projetil)


    def atualizar_ataque(self, dt):
        current_time = time.get_ticks()
        attack_duration = 300 / self.arma.velocidade
        self.attack_progress = min(1.0, (current_time - self.attack_start_time) / attack_duration)

        if self.attack_progress >= 1.0:
            self.attacking = False
            self.sword_trail = []
            return
        
        
        # Adiciona posição atual ao rastro
        angle = self.calcular_angulo(mouse.get_pos())
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)
        base_x = centro_jogador[0] + math.cos(angle) * (self.radius - 5)
        base_y = centro_jogador[1] + math.sin(angle) * (self.radius - 5)
        
        self.sword_trail.append((base_x, base_y, self.sword_angle))
        if len(self.sword_trail) > self.max_trail_length:
            self.sword_trail.pop(0)


        # Arco de ataque aumentado (210 graus)
        swing_angle = self.sword_start_angle + self.sword_arc * self.attack_progress
        self.sword_angle = self.base_sword_angle + swing_angle * self.attack_direction

    def adicionarItem(self, item):
        if isinstance(item, Item):
            item.aplicar_em(self)
            if item not in self.itens:
                self.itens[item] = 1
            else:
                pass
        else:
            self.itemAtivo = item

    def criar_projetil(self, mouse_pos, dano,cor):
        angle = self.calcular_angulo(mouse_pos)
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)
        velocidade = 0.8

        self.projeteis.append({
            "x": centro_jogador[0],
            "y": centro_jogador[1],
            "vx": math.cos(angle) * velocidade,
            "vy": math.sin(angle) * velocidade,
            "color": cor,
            "lifetime": 1000,
            "size": 10,
            "dano": dano,
            "raio_hitbox": 8
        })

    def calcular_angulo(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        dx = mouse_x - (self.x + 32)
        dy = mouse_y - (self.y + 32)
        return math.atan2(dy, dx)

    def get_rotated_rect_ataque(self, mouse_pos):
        angle = self.calcular_angulo(mouse_pos)
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)
        base_x = centro_jogador[0] + math.cos(angle) * (self.radius + 15)
        base_y = centro_jogador[1] + math.sin(angle) * (self.radius + 15)

        hitbox_surf = Surface(self.hitbox_arma, SRCALPHA)
        draw.rect(hitbox_surf, (255, 0, 0), hitbox_surf.get_rect(), width=1)

        # Rotação idêntica à da espada
        temp_surface = Surface((hitbox_surf.get_width() * 2, hitbox_surf.get_height() * 2), SRCALPHA)
        temp_surface.blit(hitbox_surf, (temp_surface.get_width() // 2 - self.sword_pivot[0],
                                        temp_surface.get_height() // 2 - self.sword_pivot[1]))

        rotated_hitbox = transform.rotate(temp_surface, -self.sword_angle)
        rotated_rect = rotated_hitbox.get_rect(center=(base_x, base_y))

        return rotated_hitbox, rotated_rect

    def desenhar(self, tela, mouse_pos):
        angle = self.calcular_angulo(mouse_pos)
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)
        base_x = centro_jogador[0] + math.cos(angle) * (self.radius - 5)
        base_y = centro_jogador[1] + math.sin(angle) * (self.radius - 5)

        if not self.attacking:
            self.base_sword_angle = math.degrees(angle) - 90
            self.sword_angle = self.base_sword_angle

        # Desenho da espada
        sword_img = self.sword.copy()
        temp_surface = Surface((sword_img.get_width() * 2, sword_img.get_height() * 2), SRCALPHA)
        temp_surface.blit(sword_img, (temp_surface.get_width() // 2 - self.sword_pivot[0],
                                      temp_surface.get_height() // 2 - self.sword_pivot[1]))
        rotated_surface = transform.rotate(temp_surface, -self.sword_angle)
        final_rect = rotated_surface.get_rect(center=(base_x, base_y))
        tela.blit(rotated_surface, final_rect.topleft)

        # Rastros do dash
        for rastro in self.rastros:
            imagem = rastro["imagem"].copy()
            alpha = max(0, int(255 * (rastro["tempo"] / 200)))
            imagem.set_alpha(alpha)
            tela.blit(imagem, rastro["pos"])

        #EFEITO PARA A ESPADA
        for i, (x, y, angle) in enumerate(self.sword_trail):
                alpha = int(self.trail_alpha * (i/len(self.sword_trail)))
                sword_copy = self.sword.copy()
                sword_copy.set_alpha(alpha)
                
                temp_surface = Surface((sword_copy.get_width() * 2, sword_copy.get_height() * 2), SRCALPHA)
                temp_surface.blit(sword_copy, (temp_surface.get_width() // 2 - self.sword_pivot[0],
                                            temp_surface.get_height() // 2 - self.sword_pivot[1]))
                rotated_surface = transform.rotate(temp_surface, -angle)
                final_rect = rotated_surface.get_rect(center=(x, y))
                tela.blit(rotated_surface, final_rect.topleft)



        # Personagem
        frame = self.frame_atual.copy()
        if self.foi_atingido and time.get_ticks() - self.tempo_atingido < 250:
            frame.fill((255, 255, 255), special_flags=BLEND_RGB_ADD)
        tela.blit(frame, self.player_rect.topleft)

        #projeteis

        for projetil in self.projeteis:
            s = Surface((projetil["size"], projetil["size"]), SRCALPHA)
            radius = projetil["size"] // 2
            color = projetil["color"]  # Assumindo que a cor já inclui alpha ou não é necessário
            draw.circle(s, color, (projetil["size"] // 2, projetil["size"] // 2), radius)
            tela.blit(s, (projetil["x"] - projetil["size"] // 2, projetil["y"] - projetil["size"] // 2))




        # Hitbox de ataque (debug)
        rotated_hitbox, rotated_rect = self.get_rotated_rect_ataque(mouse_pos)
        #tela.blit(rotated_hitbox, rotated_rect)

        self.sistemaparticulas.draw(tela)

    def get_hitbox(self):
        rect = Rect(self.player_img.get_rect(topleft=(self.x, self.y)))
        return rect

    def get_velocidade(self):
        return (self.vx, self.vy)

    def set_velocidade_x(self, vx):
        self.vx = vx

    def set_velocidade_y(self, vy):
        self.vy = vy

    def mover_se(self, pode_x, pode_y, dx, dy):
        if pode_x:
            self.player_rect.x += dx
        if pode_y:
            self.player_rect.y += dy
        self.x, self.y = self.player_rect.topleft

    def medidorCombo(self):
        self.arma.comboMult *= 1.1 ** self.hits

    def infoArma(self):
        print(
            f'Dano: {self.arma.dano}\nRapidez: {self.arma.velocidade}\nLife steal: {self.arma.lifeSteal}\nChance de Crítico: {self.arma.chanceCritico}\nDano do Crítico: {self.arma.danoCriticoMod * self.arma.dano}')
        print("Nome: ", self.arma.nome)
        print(self.velocidadeMov)

    def criar_efeito_sangue(self, x, y):
        for _ in range(5):
            angle = uniform(0, math.pi * 2)
            speed = uniform(1, 1)
            self.sistemaparticulas.add_particle(
                x, y,
                (200, 0, 0),
                (math.cos(angle) * speed, math.sin(angle) * speed),
                500,
                randint(8, 10)
            )


    def ataque_espadaPrincipal(self, inimigos, mouse_pos, dt):
        current_time = time.get_ticks()
        cooldown = self.cooldown_ataque_base / self.arma.velocidade

        if current_time - self.ultimo_ataque < cooldown:
            return

        self.ultimo_ataque = current_time
        self.attacking = True
        self.attack_start_time = current_time
        self.attack_progress = 0
        angle = self.calcular_angulo(mouse_pos)
        self.base_sword_angle = math.degrees(angle) - 90
        self.attack_direction = 1 if random() > 0.5 else -1

        _, hitbox_espada = self.get_rotated_rect_ataque(mouse_pos)
        hit_landed = False

        if current_time - self.tempo_ultimo_hit > self.tempo_max_combo:
            self.hits = 0
            self.arma.comboMult = 1.0

        for inimigo in inimigos:
            if inimigo.vivo and inimigo.get_hitbox().colliderect(hitbox_espada):
                hit_landed = True
                inimigo.anima_hit = True
                self.hits += 1
                self.tempo_ultimo_hit = current_time
                self.arma.comboMult = 1.0 + (0.1 * self.hits)
                self.arma.ataquePrincipal(inimigo)
                inimigo.ultimo_dano_tempo = current_time
                self.hp = min(self.hp + self.arma.lifeSteal, self.hpMax)
                dx = inimigo.x - self.x
                dy = inimigo.y - self.y
                inimigo.aplicar_knockback(dx, dy, intensidade=4)
                self.criar_efeito_sangue(hitbox_espada.centerx, hitbox_espada.centery)
                display.flip()
                time.delay(50)

        if not hit_landed and current_time - self.tempo_ultimo_hit > self.tempo_max_combo:
            self.hits = 0
            self.arma.comboMult = 1.0

    def ataque_espadaSecundario(self, inimigos, mouse_pos, dt):
        current_time = time.get_ticks()

        cooldown = self.cooldown_ataque_base / self.arma.velocidade

        if current_time - self.ultimo_ataque < cooldown:
            return
        if self.arma.secEhAtaque:
            if not self.arma.ehRanged:
                self.ultimo_ataque = current_time
                self.attacking = True
                self.attack_start_time = current_time
                self.attack_progress = 0
                angle = self.calcular_angulo(mouse_pos)
                self.base_sword_angle = math.degrees(angle) - 90
                self.attack_direction = 1 if random() > 0.5 else -1

                _, hitbox_espada = self.get_rotated_rect_ataque(mouse_pos)
                for inimigo in inimigos:
                    if inimigo.vivo:
                        if inimigo.get_hitbox().colliderect(hitbox_espada):
                            inimigo.anima_hit = True
                            self.arma.ataqueSecundario(inimigo,self)
                            dx = inimigo.x - self.x
                            dy = inimigo.y - self.y
                            inimigo.aplicar_knockback(dx, dy, intensidade=0.5)
            else:
                if self.arma.ataqueTipo == "melee":
                    self.attacking = True
                    self.attack_start_time = current_time
                    self.attack_progress = 0
                    angle = self.calcular_angulo(mouse_pos)
                    self.base_sword_angle = math.degrees(angle) - 90
                    self.attack_direction = 1 if random() > 0.5 else -1
                self.ultimo_ataque = current_time
                self.arma.ataqueSecundario(self, mouse_pos)
        else:
            self.arma.ataqueSecundario(self)

    def tomar_dano(self, valor):
        now = time.get_ticks()
        if now - self.ultimo_dano < self.invencibilidade:
            return
        self.ultimo_dano = now
        self.hp -= valor * self.modificadorDanoRecebido
        self.foi_atingido = True
        self.tempo_atingido = time.get_ticks()