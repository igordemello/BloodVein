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
from screen_shake import screen_shaker
from som import som
from som import GerenciadorDeMusica
from som import musica



class Player():
    def __init__(self, x, y, largura, altura, hp=100, st=100, velocidadeMov=0.5, sprite='hero.png', arma=None):
        # animações
        self.hit_landed = None
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
            "idle": self.carregar_animacao("assets/Player/IDLE.png"),
            "idle_costas": self.carregar_animacao("assets/Player/IDLE_COSTAS.png"),
            "idle_lado1": self.carregar_animacao("assets/Player/IDLE_LADO.png"),
            "idle_lado2": [transform.flip(img, True, False) for img in
                         self.carregar_animacao("assets/Player/IDLE_LADO.png")],
        }

        self.atributos = {
            "forca" : 1, #influencia DANO DA ARMA, DANO DO CRÍTICO
            "destreza": 1, #influencia VELOCIDADE DE ATAQUE DA ARMA
            "agilidade": 1, # influencia VELOCIDADE DE MOVIMENTO DO PERSONAGEM
            "vigor": 1, #influencia VELOCIDADE DO DECAIMENTO
            "resistencia": 1, #influencia DANO RECEBIDO
            "estamina": 1, #influencia COOLDOWN DE DASH, GASTO E COOLDOWN STAMINA
            "sorte": 1, #influencia CHANCE DE CRÍTICO E UM POUCO DE TUDO
        }
        #1-2 normal / 3-4 melhorzinho / 5-6 bom / 7-8 muito bom / 9-10 peak
        self.hp = hp
        self.hpMax = 100
        self.rate = 1 - (self.atributos["vigor"]/20) #decaimento da vida - max em 0.5
        self.rateSt = 1 + ((self.atributos["estamina"]*3)/10) #velocidade que a stamina recupera - max em 4
        self.velocidadeMov = velocidadeMov + (self.atributos["agilidade"]/20) #velocidade de movimento - inicial : 0.5 // max : 1
        self.custoDash = 2.75 - ((self.atributos["estamina"] - 1) * (0.75 / 9)) #custo do dash - inicial : 2.75 // max : 2
        self.modificadorDanoRecebido = 1 - (self.atributos["resistencia"]/20) #modificador de resistencia - inicial : 1 // max : 0.5
        self.invencibilidade = int(1500 + ((self.atributos["resistencia"] - 1) * (500 / 9))) #tempo de invencibilidade - inicial : 1500 // max : 2000
        self.cooldown_st = round(3222.22 - (self.atributos["estamina"] * 222.22)) #cooldown de stamina - inicial : 3000 // max : 1000
        self.dash_cooldown_max = int(1000 - ((self.atributos["estamina"] - 1) * (750 / 9))) #cooldown entre dashes - inicial : 1000 // max :  250
        self.dash_duration_max = int(150 + ((self.atributos["estamina"] - 1) * (250 / 9))) #duração máxima do dash - inicial : 150 // max : 400

        self.gameOver = False

        self.animacoes_principais = 'esquerdadireitabaixocima'
        self.anim_direcao = "baixo"
        self.anim_frame = 0
        self.tempo_animacao = 0
        self.tempo_por_frame = 100
        self.frame_atual = self.animacoes[self.anim_direcao][self.anim_frame]
        self.rastros = []

        self.sistemaparticulas = ParticleSystem()
        self.lista_mods = ListaMods()
        #ARMA
        self.arma = arma if arma else EspadaEstelar("comum", self.lista_mods)

        self.telaSangue = image.load('assets/UI/sangueTelaDano.png').convert_alpha()
        self.telaSangue_alpha = 0
        self.telaSangue_surface = None

        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.ultimo_uso = 0
        self.revives = 0
        self.ultimo_dano = 0
        self.foi_atingido = False
        self.tempo_atingido = 0
        self.itens = {}
        self.itemAtivo = None
        self.salaAtivoUsado = None
        self.itemAtivoEsgotado = None
        self.st = st

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

        self.is_dashing = False
        self.last_dash_time = 0
        self.dash_direcao = None
        self.parado_desde = 0
        self.ativo_ultimo_uso = 0

        self.sword = transform.scale(transform.flip(image.load(self.arma.sprite).convert_alpha(), True, True),
                                     (self.arma.size))
        self.sword_pivot = self.arma.pivot
        self.sword_angle = 0
        self.attacking = False
        self.attack_start_time = 0
        self.attack_direction = 1
        self.attack_progress = 0
        self.base_sword_angle = 0
        self.sword_arc = 210
        self.sword_start_angle = -105

        # Sistema de rastro melhorado
        self.sword_trail_particles = []
        self.trail_max_particles = 50
        self.trail_fade_speed = 15
        self.trail_size_variation = 0
        self.trail_spawn_rate = 1
        self.trail_start_alpha = 130

        self.projetil_trail_particles = []
        self.trail_projetil_max = 5
        self.trail_projetil_fade = 25

        self.last_attack_direction = -1

        self.dano_recebido_tempo = 0

        self.projeteis = []
        self.aoe = None
        self.hits_projetil = 0
        self.tempo_ultimo_hit_projetil = 0

        self.cooldown_ataque_base = self.arma.cooldown
        self.ultimo_ataque = 0
        self.sprite_dano = self.frame_atual.copy()
        self.sprite_dano.fill((255, 255, 255), special_flags=BLEND_RGB_ADD)

        clock = time.Clock()
        self.dt = clock.get_time()
        self.player_img = self.frame_atual
        self.player_rect = Rect(self.x, self.y, 60, 120)
        self.dx = 0
        self.dy = 0

        self.travado = False

        self.som_dash = True

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
        
        if self.travado:
            return
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
            if self.som_dash == True:
                som.tocar('dash')
                self.som_dash = False
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
                if self.som_dash == False:
                    self.som_dash = True
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
            self.tempo_por_frame = 100
            self.tempo_animacao += dt
            if self.tempo_animacao > self.tempo_por_frame:
                self.tempo_animacao = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.animacoes[self.anim_direcao]) and self.anim_direcao in self.animacoes_principais:
                    self.anim_frame = 4
        else:
            angulo = self.calcular_angulo(mouse.get_pos())
            angulo_deg = math.degrees(angulo) % 360


            if 45 < angulo_deg <= 135:
                self.anim_direcao = "idle"
            elif 135 < angulo_deg <= 225:
                self.anim_direcao = "idle_lado2"
            elif 225 < angulo_deg <= 315:
                self.anim_direcao = "idle_costas"
            else:
                self.anim_direcao = "idle_lado1"

            self.tempo_animacao += dt
            self.tempo_por_frame = 200
            if self.tempo_animacao > self.tempo_por_frame:
                self.tempo_animacao = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.animacoes[self.anim_direcao]) and self.anim_direcao in self.animacoes_principais:
                    self.anim_frame = 0

        self.hp -= 0.05 * self.rate

        if current_time - self.last_dash_time >= self.cooldown_st:
            self.st += 0.7 * self.rateSt

        if self.hp < 0:
            self.hp = 0
        if self.hp > 100:
            self.hp = 100
        if self.st < 0:
            self.st = 0
        if self.st > 100:
            self.st = 100

        '''
        if self.hp == 0:
            self.gameOver = True
        '''

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

        if self.hits_projetil > 0 and time.get_ticks() - self.tempo_ultimo_hit_projetil > self.tempo_max_combo:
            self.hits_projetil = 0
            self.arma.comboMult = 1

        for projetil in self.projeteis[:]:
            if len(projetil["trail"]) < self.trail_projetil_max or random() < 0.4:
                projetil["trail"].append({
                    "x": projetil["x"],
                    "y": projetil["y"],
                    "alpha": randint(150, 200),  # Variação de transparência
                    "angle": projetil["angulo"] + randint(-5, 5),  # Pequena variação angular
                    "lifetime": randint(200, 255),  # Variação de tempo de vida
                    "scale": 0.5 + random() * 0.5  # Variação de escala
                })

            for part in projetil["trail"][:]:
                part["alpha"] = max(0, part["alpha"] - self.trail_projetil_fade)
                if part["alpha"] <= 0:
                    projetil["trail"].remove(part)

            projetil["x"] += projetil["vx"] * dt
            projetil["y"] += projetil["vy"] * dt
            projetil["lifetime"] -= dt
            if projetil["lifetime"] <= 0:
                self.projeteis.remove(projetil)
        if move_input:
            for _ in range(1):  # duas partículas
                offset_x = randint(-10, 5)
                offset_y = randint(-5, 5)
                self.sistemaparticulas.add_particle(
                    self.player_rect.centerx + offset_x,
                    self.player_rect.centery + offset_y + 40,  # um pouco mais pra baixo
                    (255, 255, 255),  # cor branca
                    (uniform(-0.05, 0.05), uniform(-0.05, 0.05)),  # leve movimento
                    lifetime=200,  # vida curta (ms)
                    size=3  # tamanho da partícula
                )

    def atualizar_ataque(self, dt):
        current_time = time.get_ticks()
        attack_duration = 300 / self.arma.velocidade
        self.attack_progress = min(1.0, (current_time - self.attack_start_time) / attack_duration)

        if self.attack_progress >= 1.0:
            self.attacking = False
            self.sword_trail_particles = []
            return 

        angle = self.calcular_angulo(mouse.get_pos())
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)
        base_x = centro_jogador[0] + math.cos(angle) * (self.radius - 5)
        base_y = centro_jogador[1] + math.sin(angle) * (self.radius - 5)

        # Adiciona nova partícula ao rastro
        if (len(self.sword_trail_particles) < self.trail_max_particles and
            random() < self.trail_spawn_rate):
            size_variation = 1 + (random() - 0.5) * self.trail_size_variation
            self.sword_trail_particles.append({
                'x': base_x,
                'y': base_y,
                'angle': self.sword_angle,
                'size': size_variation,
                'alpha': self.trail_start_alpha,  # Usando o valor definido no init
                'lifetime': 255,
                'color_mod': (min(255, 200 + randint(0, 55)),
                              min(255, 200 + randint(0, 55)),
                              min(255, 200 + randint(0, 55)))
            })

        for particle in self.sword_trail_particles[:]:
            particle['alpha'] = max(0, particle['alpha'] - self.trail_fade_speed)
            particle['lifetime'] -= self.trail_fade_speed
            if particle['lifetime'] <= 0:
                self.sword_trail_particles.remove(particle)

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

    def criar_projetil(self, mouse_pos, dano, cor, sprite=None, tamanho=10, velocidade=0.8, lifetime=1000,
                       angulo_personalizado=None):
        angle = self.calcular_angulo(mouse_pos)
        centro_jogador = (self.player_rect.centerx, self.player_rect.centery)

        if angulo_personalizado is not None:
            angle = angulo_personalizado

        if sprite:
            distancia = self.radius + sprite.get_width() // 2
            sprite_original = sprite
        else:
            distancia = self.radius + tamanho // 2
            sprite_original = None

        start_x = centro_jogador[0] + math.cos(angle) * distancia
        start_y = centro_jogador[1] + math.sin(angle) * distancia

        projetil = {
            "x": start_x,
            "y": start_y,
            "vx": math.cos(angle) * velocidade,
            "vy": math.sin(angle) * velocidade,
            "dano": dano,
            "lifetime": lifetime,
            "raio_hitbox": tamanho // 2 if not sprite else max(sprite.get_width(), sprite.get_height()) // 2,
            "trail": [],  # Partículas de rastro para este projétil
            "sprite_original": sprite_original,
            "angulo": math.degrees(angle) - 90  # Ângulo em graus para rotação
        }

        if sprite:
            projetil["sprite"] = sprite
        else:
            projetil["cor"] = cor
            projetil["tamanho"] = tamanho

        self.projeteis.append(projetil)

    def criarAOE(self, mouse_pos, tamanho):
        mouse_x, mouse_y = mouse_pos
        rect = Rect(0, 0, tamanho, tamanho)
        rect.center = (mouse_x, mouse_y)
        s = Surface((tamanho, tamanho), SRCALPHA)
        tempoCriacao = time.get_ticks()
        return s, rect,tamanho,tempoCriacao

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

        for particle in sorted(self.sword_trail_particles, key=lambda p: p['alpha']):
            alpha = particle['alpha']
            if alpha <= 0:
                continue

            sword_copy = transform.scale(self.sword,
                                         (int(self.sword.get_width() * particle['size']),
                                          int(self.sword.get_height() * particle['size'])))

            colored_sword = Surface(sword_copy.get_size(), SRCALPHA)
            colored_sword.blit(sword_copy, (0, 0))
            colored_sword.fill(particle['color_mod'], special_flags=BLEND_MULT)
            colored_sword.set_alpha(alpha)

            temp_surface = Surface((colored_sword.get_width() * 2, colored_sword.get_height() * 2), SRCALPHA)
            temp_surface.blit(colored_sword,
                              (temp_surface.get_width() // 2 - self.sword_pivot[0],
                               temp_surface.get_height() // 2 - self.sword_pivot[1]))

            rotated_surface = transform.rotate(temp_surface, -particle['angle'])
            final_rect = rotated_surface.get_rect(center=(particle['x'], particle['y']))
            tela.blit(rotated_surface, final_rect.topleft)

        self.sistemaparticulas.draw(tela)

        sword_img = self.sword.copy()
        temp_surface = Surface((sword_img.get_width() * 2, sword_img.get_height() * 2), SRCALPHA)
        temp_surface.blit(sword_img, (temp_surface.get_width() // 2 - self.sword_pivot[0],
                                      temp_surface.get_height() // 2 - self.sword_pivot[1]))
        rotated_surface = transform.rotate(temp_surface, -self.sword_angle)
        final_rect = rotated_surface.get_rect(center=(base_x, base_y))
        tela.blit(rotated_surface, final_rect.topleft)

        frame = self.frame_atual.copy()
        if self.foi_atingido and time.get_ticks() - self.tempo_atingido < 250:
            frame.fill((255, 255, 255), special_flags=BLEND_RGB_ADD)
        img_rect = frame.get_rect(center=self.player_rect.center)
        tela.blit(frame, img_rect.topleft)

        if self.aoe is not None:
            s, rectAoe,tamanho,tempoCriacao = self.aoe
            tempo_atual = time.get_ticks()
            if tempo_atual - tempoCriacao < 2000:
                s.fill((0, 0, 0, 0))
                draw.rect(s, (255, 228, 76, 20), s.get_rect(), border_radius=int(tamanho / 2))
                tela.blit(s, rectAoe.topleft)
            else:
                self.aoe = None


        #projeteis

        for projetil in self.projeteis:
            for part in projetil["trail"]:
                if "sprite" in projetil:
                    trail_sprite = projetil["sprite_original"].copy()
                    trail_sprite.set_alpha(part["alpha"])
                    trail_sprite = transform.scale(projetil["sprite_original"],
                                                   (int(projetil["sprite_original"].get_width() * part["scale"]),
                                                    int(projetil["sprite_original"].get_height() * part["scale"])))

                    rotated = transform.rotate(trail_sprite, -part["angle"])
                    rect = rotated.get_rect(center=(part["x"], part["y"]))
                    tela.blit(rotated, rect.topleft)

            if "sprite" in projetil:
                sprite_rotacionado = transform.rotate(projetil["sprite_original"], -projetil["angulo"])
                rect = sprite_rotacionado.get_rect(center=(projetil["x"], projetil["y"]))
                tela.blit(sprite_rotacionado, rect.topleft)
            else:
                s = Surface((projetil["tamanho"], projetil["tamanho"]), SRCALPHA)
                draw.circle(s, projetil["cor"],
                            (projetil["tamanho"] // 2, projetil["tamanho"] // 2),
                            projetil["tamanho"] // 2)
                tela.blit(s, (projetil["x"] - projetil["tamanho"] // 2,
                              projetil["y"] - projetil["tamanho"] // 2))




        # Hitbox de ataque (debug)
        rotated_hitbox, rotated_rect = self.get_rotated_rect_ataque(mouse_pos)
        #tela.blit(rotated_hitbox, rotated_rect)


        if hasattr(self, 'dano_recebido') and time.get_ticks() - self.dano_recebido_tempo < 500:
            if self.telaSangue_alpha > 0:
                self.telaSangue_alpha = max(0, 255 - (time.get_ticks() - self.dano_recebido_tempo) * 1.02)
                self.telaSangue_surface.set_alpha(int(self.telaSangue_alpha))
                tela.blit(self.telaSangue_surface, (0, 0))

            cor = (255, 0, 0)
            tamanho_fonte = 48
            fonte_atual = font.Font('assets/Fontes/KiwiSoda.ttf', tamanho_fonte)
            texto_str = f"-{self.dano_recebido:.1f}"

            pos_x = 108
            pos_y = 440 - ((time.get_ticks() - self.dano_recebido_tempo) / 4)

            outline_color = (0, 0, 0)
            outline_size = 1
            for x_offset in [-outline_size, 0, outline_size]:
                for y_offset in [-outline_size, 0, outline_size]:
                    if x_offset == 0 and y_offset == 0:
                        continue
                    outline_text = fonte_atual.render(texto_str, True, outline_color)
                    tela.blit(outline_text, (pos_x - outline_text.get_width() / 2 + x_offset, pos_y + y_offset))

            dano_text = fonte_atual.render(texto_str, True, cor)
            tela.blit(dano_text, (pos_x - dano_text.get_width() / 2, pos_y))





    def get_hitbox(self):
        return self.player_rect

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

    def infoArma(self):
        print(
            f'Dano: {self.arma.dano}\nRapidez: {self.arma.velocidade}\nLife steal: {self.arma.lifeSteal}\nChance de Crítico: {self.arma.chanceCritico}\nDano do Crítico: {self.arma.danoCriticoMod * self.arma.dano}')
        print("Nome: ", self.arma.nome)
        print(self.atributos["forca"])

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
        self.hit_landed = False

        if current_time - self.ultimo_ataque < cooldown:
            return

        if self.arma.ataqueTipo != "ranged":
            self.ultimo_ataque = current_time
            self.attacking = True
            self.attack_start_time = current_time
            self.attack_progress = 0
            angle = self.calcular_angulo(mouse_pos)
            self.base_sword_angle = math.degrees(angle) - 90

            self.last_attack_direction *= -1
            self.attack_direction = self.last_attack_direction

            _, hitbox_espada = self.get_rotated_rect_ataque(mouse_pos)

            if current_time - self.tempo_ultimo_hit > self.tempo_max_combo:
                self.hits = 0
                self.arma.comboMult = 1.0

            for inimigo in inimigos:
                if inimigo.vivo and inimigo.get_hitbox().colliderect(hitbox_espada):
                    self.hit_landed = True

                    screen_shaker.start(intensity=9, duration=150)

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

            if not self.hit_landed and current_time - self.tempo_ultimo_hit > self.tempo_max_combo:
                self.hits = 0
                self.arma.comboMult = 1.0
        else:
            self.arma.ataquePrincipal(self, mouse_pos)
            self.ultimo_ataque = current_time


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
            elif self.arma.ehAOE:
                self.aoe = self.arma.ataqueSecundario(self, mouse_pos)
                self.ultimo_ataque = current_time
                self.attacking = True
                self.attack_start_time = current_time
                self.attack_progress = 0
                angle = self.calcular_angulo(mouse_pos)
                self.base_sword_angle = math.degrees(angle) - 90
                self.attack_direction = 1 if random() > 0.5 else -1

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
        self.tempo_atingido = now
        self.dano_recebido_tempo = now
        self.dano_recebido = valor * self.modificadorDanoRecebido
        self.telaSangue_alpha = 255
        screen_shaker.start(intensity=4, duration=150)
        if self.telaSangue_surface is None:
            self.telaSangue_surface = self.telaSangue.copy()


    def atualizar_arma(self):
        self.sword = transform.scale(transform.flip(image.load(self.arma.sprite).convert_alpha(), True, True),
                                     (self.arma.size))
        self.sword_pivot = self.arma.pivot
        self.cooldown_ataque_base = self.arma.cooldown
        self.radius = self.arma.radius - 50
        self.hitbox_arma = self.arma.range


    def atualizar_atributos(self):
        #dano da arma e dano do crítico - força
        self.arma.dano *= 1 + (self.atributos["forca"] - 1) / 9#mínimo é o proprio dano da arma, máximo é o dobro
        self.arma.danoCriticoMod *=  1 + (self.atributos["forca"] - 1) / 9#mínimo é o proprioCriticoMod, maximo é o dobro

        #velocidade de ataque da arma - destreza
        self.arma.velocidade *= 1 + ((self.atributos["destreza"] - 1) / 9) * 0.5

        #chance de critico - sorte
        self.arma.chanceCritico *= 1 + ((self.atributos["sorte"] - 1) / 9) * 3
        if hasattr(self.arma, "criticoOg"):
            self.arma.criticoOg *= 1 + ((self.atributos["sorte"] - 1) / 9) * 3

        self.rate = 1 - (self.atributos["vigor"] / 20)  # decaimento da vida - max em 0.5
        self.rateSt = 1 + ((self.atributos["estamina"] * 3) / 10)  # velocidade que a stamina recupera - max em 4
        self.velocidadeMov = self.velocidadeMov + (
                    self.atributos["agilidade"] / 20)  # velocidade de movimento - inicial : 0.5 // max : 1
        self.custoDash = 2.75 - (
                    (self.atributos["estamina"] - 1) * (0.75 / 9))  # custo do dash - inicial : 2.75 // max : 2
        self.modificadorDanoRecebido = 1 - (
                    self.atributos["resistencia"] / 20)  # modificador de resistencia - inicial : 1 // max : 0.5
        self.invencibilidade = int(1500 + ((self.atributos["resistencia"] - 1) * (
                    500 / 9)))  # tempo de invencibilidade - inicial : 1500 // max : 2000
        self.cooldown_st = round(
            3222.22 - (self.atributos["estamina"] * 222.22))  # cooldown de stamina - inicial : 3000 // max : 1000
        self.dash_cooldown_max = int(1000 - ((self.atributos["estamina"] - 1) * (
                    750 / 9)))  # cooldown entre dashes - inicial : 1000 // max :  250
        self.dash_duration_max = int(
            150 + ((self.atributos["estamina"] - 1) * (250 / 9)))  # duração máxima do dash - inicial : 150 // max : 400


    def get_save_data(self):
        return {
        'position': [self.x, self.y],
        'stats': {
            'hp': self.hp,
            'hpMax': self.hpMax,
            'st': self.st,
            'almas': self.almas,
            'velocidadeMov': self.velocidadeMov,
            'atributos' : self.atributos
        },
        'itens': [item.id for item in self.itens],
        'itemAtivo': self.itemAtivo.id if self.itemAtivo else None,
        'arma': self.arma.get_save_data() if hasattr(self.arma, 'get_save_data') else None
    }


    def load_save_data(self, data, conjunto_itens, lista_mods):
        self.x, self.y = data['position']
        self.player_rect.topleft = self.x, self.y

        stats = data['stats']
        self.hp = stats['hp']
        self.hpMax = stats['hpMax']
        self.st = stats['st']
        self.almas = stats['almas']
        self.velocidadeMov = stats['velocidadeMov']
        self.atributos = stats['atributos']

        self.itens = {}
        for item_id in data['itens']:
            item = conjunto_itens.itens_por_id[item_id]
            self.adicionarItem(item)

        if data['itemAtivo']:
            self.itemAtivo = conjunto_itens.itens_por_id[data['itemAtivo']]

        if data['arma']:
            arma_class = globals().get(data['arma']['tipo'])
            if arma_class:
                self.arma = arma_class(data['arma']['raridade'], lista_mods)
                self.arma.load_save_data(data['arma'], lista_mods)
                self.atualizar_arma()