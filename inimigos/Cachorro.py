from pygame import *
import math
import random
from pygame import time
from inimigo import Inimigo
from utils import resource_path 
from pygame.locals import USEREVENT

class Cerbero(Inimigo):
    def __init__(self, x, y, largura=256, altura=256, hp=5000, velocidade=3, dano=40):
        super().__init__(x, y, largura, altura, hp, velocidade, dano)
        self.hp = hp
        self.hp_max = hp
        self.tipo_colisao = "terrestre"
        self.estado = "perseguindo"  # Estados: perseguindo, patada, grito, cospe_fogo


        self.bola_fogo = transform.scale(
            image.load('./assets/Enemies/Bola_de_Fogo_Ataque_atena.png').convert_alpha(),
            (40, 40)
        )
                
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
        
        # Projéteis
        self.bolas_fogo = []
        self.velocidade_bola_fogo = 4
        self.duracao_bola_fogo = 4000
        self.dano_bola_fogo = 20  # Adicionado o atributo que estava faltando
        
        # Lava
        self.lava_posicoes = []
        self.tamanho_lava = (120, 120)
        self.duracao_lava = 5000
        
        # Configurações de hitbox
        self.hitbox_patada = {
            "esquerda": Rect(0, 0, 80, self.altura),
            "direita": Rect(0, 0, 80, self.altura),
            "baixo": Rect(0, 0, self.largura, 80)
        }
        
        # Referência ao jogador (será definida depois)
        self.player = None

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

    def trocar_estado(self, novo_estado):
        if self.estado != novo_estado:
            self.estado = novo_estado
            self.frame_index = 0
            self.frame_time = 0
            
            # Resetar contadores específicos
            if novo_estado == "patada":
                self.contador_patadas = 0
            elif novo_estado == "cospe_fogo":
                self.contador_cuspe = 0

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animacoes[self.animacao_atual])

    def atualizar(self, player_pos, tela, mapa_matriz,offset):
        if not self.vivo:
            return

        now = time.get_ticks()
        
        # Atualiza a animação
        self.atualizar_animacao()

        # Lógica de estados
        if self.estado == "perseguindo":
            self.executar_perseguir(player_pos, now)
        elif self.estado == "patada":
            self.executar_patada(player_pos, now)
        elif self.estado == "grito":
            self.executar_grito(now, player_pos)
        elif self.estado == "cospe_fogo":
            self.executar_cuspe_fogo(now, player_pos)

        # Atualizar projéteis e lava
        self.atualizar_bolas_fogo(now)
        self.atualizar_lava(now)

        # Atualizar posição da hitbox
        self.rect.topleft = (self.x, self.y)

    def executar_perseguir(self, player_pos, now):
        dx = player_pos[0] - (self.x + self.largura/2)
        dy = player_pos[1] - (self.y + self.altura/2)
        distancia = math.hypot(dx, dy)

        # Escolhe o ataque baseado na distância e cooldowns
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
            # Persegue o jogador
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
        
        # Frame de impacto
        if self.frame_index == 3 and not hasattr(self, 'patada_atingiu'):
            # Configura as hitboxes de patada
            self.hitbox_patada["esquerda"].topleft = (self.x - 80, self.y)
            self.hitbox_patada["direita"].topleft = (self.x + self.largura, self.y)
            self.hitbox_patada["baixo"].topleft = (self.x, self.y + self.altura)
            
            # Verifica colisão com o jogador
            player_rect = Rect(player_pos[0], player_pos[1], 64, 64)
            
            for direcao, hitbox in self.hitbox_patada.items():
                if player_rect.colliderect(hitbox):
                    if hasattr(self, "dar_dano") and callable(self.dar_dano):
                        self.dar_dano()
                    # Desativa habilidades por 3s
                    event.post(event.Event(USEREVENT+10, {}))  # Evento para liberar depois
                    if self.player:
                        pass
            
            self.patada_atingiu = True

        # Final da animação
        if self.frame_index >= len(self.animacoes["patada"]) - 1:
            self.trocar_estado("perseguindo")
            if hasattr(self, 'patada_atingiu'):
                del self.patada_atingiu


    def executar_grito(self, now, player_pos):
        self.animacao_atual = "grito"

        # Frame do grito
        if self.frame_index == 4 and not hasattr(self, 'grito_aplicado'):
            # Armazena a velocidade original do jogador, se ainda não tiver sido salva
            if not hasattr(self.player, 'velocidade_original_grito'):
                self.player.velocidade_original_grito = self.player.velocidadeMov

            # Aplica lentidão e paralisia
            self.player.velocidadeMov = self.player.velocidade_original_grito * 0.4
            self.player.travado = True

            # Inicia timers para liberar paralisia e restaurar velocidade
            time.set_timer(USEREVENT + 11, 1000, True)   # Libera paralisia após 1s
            time.set_timer(USEREVENT + 12, 5000, True)   # Restaura velocidade após 5s

            self.grito_aplicado = True

        # Final da animação
        if self.frame_index >= len(self.animacoes["grito"]) - 1:
            self.trocar_estado("perseguindo")
            if hasattr(self, 'grito_aplicado'):
                del self.grito_aplicado

    def executar_cuspe_fogo(self, now, player_pos):
        self.animacao_atual = "cospe_fogo"
        
        # Frames de cuspe
        if self.frame_index in [2, 3, 4] and self.contador_cuspe < 3:
                # Cria 3 bolas de fogo
                for i in range(3):
                    angulo = math.atan2(player_pos[1] - (self.y + self.altura/2), 
                                       player_pos[0] - (self.x + self.largura/2))
                    angulo += random.uniform(-0.2, 0.2)  # Pequena variação
                    
                    self.bolas_fogo.append({
                        'x': self.x + self.largura/2,
                        'y': self.y + self.altura/2,
                        'vx': math.cos(angulo) * self.velocidade_bola_fogo,
                        'vy': math.sin(angulo) * self.velocidade_bola_fogo,
                        'dano': self.dano_bola_fogo,
                        'criado': now
                    })
                
                # Cria área de lava
                lava_x = player_pos[0] + random.randint(-150, 150)
                lava_y = player_pos[1] + random.randint(-150, 150)
                self.lava_posicoes.append({
                    'rect': Rect(lava_x, lava_y, self.tamanho_lava[0], self.tamanho_lava[1]),
                    'criado': now
                })
                
                setattr(self, f'cuspe_{self.contador_cuspe}', True)
                self.contador_cuspe += 1

        # Final da animação
        if self.frame_index >= len(self.animacoes["cospe_fogo"]) - 1:
            self.contador_cuspe = 0
            self.trocar_estado("perseguindo")

    def atualizar_bolas_fogo(self, now):
        for bola in self.bolas_fogo[:]:
            # Atualiza posição
            bola['x'] += bola['vx']
            bola['y'] += bola['vy']
            
            # Verifica tempo de vida
            if now - bola['criado'] > self.duracao_bola_fogo:
                self.bolas_fogo.remove(bola)

    def atualizar_lava(self, now):
        for lava in self.lava_posicoes[:]:
            if now - lava['criado'] > self.duracao_lava:
                self.lava_posicoes.remove(lava)

    def desenhar(self, tela, player_pos, offset=(0, 0)):
        if not self.vivo:
            return
        
        # Desenha o boss
        frame = self.animacoes[self.animacao_atual][self.frame_index]
        if self.anima_hit:
            frame = self.aplicar_efeito_hit(frame)
        
        tela.blit(frame, (self.x + offset[0], self.y + offset[1]))
        
        # Desenha bolas de fogo
        for bola in self.bolas_fogo:
            x = int(bola['x'] + offset[0] - self.bola_fogo.get_width() // 2)
            y = int(bola['y'] + offset[1] - self.bola_fogo.get_height() // 2)
            tela.blit(self.bola_fogo, (x, y))
                
        # Desenha lava
        #for lava in self.lava_posicoes:
            #s = Surface(self.tamanho_lava, SRCALPHA)
            #s.fill((255, 50, 50, 150))  # Vermelho transparente
            #tela.blit(s, (lava['rect'].x + offset[0], lava['rect'].y + offset[1]))
        
        # Desenha barra de vida
        self.desenhar_barra_vida(tela, offset)

        now = time.get_ticks()
        if hasattr(self, 'veneno_ativo') and self.veneno_ativo:
            if now >= self.veneno_proximo_tick and self.veneno_ticks > 0:
                self.hp -= self.veneno_dano_por_tick
                self.veneno_ticks -= 1
                self.veneno_proximo_tick = now + self.veneno_intervalo

                # Inicia animação de hit como feedback visual (opcional)
                self.anima_hit = True
                self.time_last_hit_frame = now
                self.ultimo_dano = self.veneno_dano_por_tick
                self.ultimo_dano_tempo = time.get_ticks()

            if self.veneno_ticks <= 0:
                self.veneno_ativo = False

    def desenhar_barra_vida(self, tela, offset):
        largura_barra = 300
        altura_barra = 20
        x = self.x + (self.largura - largura_barra) // 2 + offset[0]
        y = self.y - 30 + offset[1]
        
        # Fundo
        draw.rect(tela, (50, 50, 50), (x, y, largura_barra, altura_barra))
        
        # Vida atual
        porcentagem = self.hp / self.hp_max
        largura_vida = int(porcentagem * largura_barra)
        draw.rect(tela, (200, 0, 0), (x, y, largura_vida, altura_barra))
        
        # Borda
        draw.rect(tela, (255, 255, 255), (x, y, largura_barra, altura_barra), 2)
        
        # Nome
        fonte = font.Font(None, 24)
        texto = fonte.render("Cerbero", True, (255, 255, 255))
        tela.blit(texto, (x + largura_barra//2 - texto.get_width()//2, y - 25))
