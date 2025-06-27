from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import randint


class Inimigo:
    def __init__(self, x, y, largura, altura, hp, velocidade=2, dano=0):
        self.alma_coletada = None
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.velocidade = velocidade

        self.particulas_dano = []


        self.ultimo_dano_tempo = 0
        self.fonte_dano = font.Font('assets/Fontes/alagard.ttf', 20)

        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_time = 0
        self.knockback_duration = 200

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)
        self.hitboxArma = (70, 100)

        self.old_x = x
        self.old_y = y

        self.hp = hp
        self.modificadorDanoRecebido = 1  # isso multiplica o dano que o jogador causa, serve pra fazer bleed e pro parry
        self.vivo = True
        self.dano = dano
        self.ultimo_dano_critico = False

        self.spritesheet = None
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 1
        self.usar_indices = [0]
        self.frames = []
        self.frame_index = 0
        self.frame_time = 0
        self.animation_speed = 0.10

        self.sprite_hit = image.load("assets/Enemies/orbTomandoDano.png").convert_alpha()
        self.frames_hit = []
        self.total_frames_hit = 4
        self.hit_frame_duration = 100
        self.frame_hit_index = 0
        self.time_last_hit_frame = 0
        self.anima_hit = False
        self.carregar_hit_sprites()

        self.vy = 0
        self.vx = 0
        self.dx = 0
        self.dy = 0

        self.rect = self.get_hitbox()

    def adicionar_particula_dano(self, x, y, valor):
        cor = (255, 50, 50)  # Vermelho
        if valor > 20:
            cor = (255, 215, 0)  # Amarelo-ouro para críticos

        for _ in range(10):  # 10 partículas
            angulo = randint(0, 360)
            velocidade = randint(1, 3)
            self.particulas_dano.append({
                'x': x,
                'y': y,
                'vx': math.cos(angulo) * velocidade,
                'vy': math.sin(angulo) * velocidade,
                'cor': cor,
                'tempo': randint(300, 500),  # 300-500ms
                'tamanho': randint(2, 5)
            })


    def get_velocidade(self):
        return (self.vx, self.vy)

    def set_velocidade_x(self, vx):
        self.vx = vx

    def set_velocidade_y(self, vy):
        self.vy = vy

    def mover_se(self, pode_x, pode_y, dx, dy):
        if pode_x:
            self.rect.x += dx
        if pode_y:
            self.rect.y += dy

        self.x, self.y = self.rect.topleft

    def carregar_sprites(self):
        if self.spritesheet:
            self.frames = [self.get_frame(i) for i in self.usar_indices]

    def carregar_hit_sprites(self):
        for i in range(self.total_frames_hit):
            rect = Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
            frame.blit(self.sprite_hit, (0, 0), rect)
            frame = transform.scale(frame, (self.largura, self.altura))
            self.frames_hit.append(frame)

    def get_frame(self, index):
        rect = Rect(index * self.frame_width, 0, self.frame_width, self.frame_height)
        frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
        frame.blit(self.spritesheet, (0, 0), rect)
        return transform.scale(frame, (self.largura, self.altura))

    def atualizar_animacao(self):
        self.frame_time += self.animation_speed
        if self.frame_time >= 1:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def aplicar_knockback(self, direcao_x, direcao_y, intensidade):
        angulo = math.atan2(direcao_y, direcao_x)
        self.knockback_x = math.cos(angulo) * intensidade
        self.knockback_y = math.sin(angulo) * intensidade
        self.knockback_time = time.get_ticks()

        # Aplica a velocidade do knockback, que será tratada com colisão
        self.set_velocidade_x(self.knockback_x)
        self.set_velocidade_y(self.knockback_y)

    def envenenar(self, duracao_em_segundos, dano_total):
        self.veneno_dano_por_tick = dano_total // 2
        self.veneno_ticks = 5
        self.veneno_intervalo = (duracao_em_segundos * 1000) // 5  # em milissegundos
        self.veneno_proximo_tick = time.get_ticks() + self.veneno_intervalo
        self.veneno_ativo = True

    def atualizar(self, player_pos, tela):
        if self.anima_hit:
            now = time.get_ticks()
            if now - self.time_last_hit_frame > self.hit_frame_duration:
                self.time_last_hit_frame = now
                self.frame_hit_index += 1
                if self.frame_hit_index >= len(self.frames_hit):
                    self.frame_hit_index = 0
                    self.anima_hit = False
                    return

        now = time.get_ticks()
        
        if now - self.knockback_time < self.knockback_duration:
            # O knockback ainda está ativo → não atualiza perseguição
            return
        else:
            # Knockback acabou → zera velocidade
            self.knockback_x = 0
            self.knockback_y = 0
            self.set_velocidade_x(0)
            self.set_velocidade_y(0)
        self.old_x = self.x
        self.old_y = self.y
        # inimigo morrendo
        if self.hp <= 0:
            self.vivo = False
            self.alma_coletada = False
            self.vx = 0
            self.vy = 0
            self.rect.topleft = (self.x, self.y)
            return

        player_x = player_pos[0]
        player_y = player_pos[1]

        self.vx = 0
        self.vy = 0

        # colocar um range máximo que ele precisa ficar do jogador
        if abs(player_x - self.x) > 100:
            self.vx = self.velocidade if player_x > self.x else -self.velocidade
        if abs(player_y - self.y) > 100:
            self.vy = self.velocidade if player_y > self.y else -self.velocidade

        rot_rect, _ = self.get_hitbox_ataque((player_x, player_y))
        player_hitbox = Rect(player_x, player_y, 64, 64)  # ou use player.get_hitbox()

        if rot_rect.colliderect(player_hitbox):
            if hasattr(self, "dar_dano") and callable(self.dar_dano):
                self.dar_dano()

        self.x,self.y = self.rect.topleft
        self.atualizar_animacao()

        if hasattr(self, 'veneno_ativo') and self.veneno_ativo:
            if now >= self.veneno_proximo_tick and self.veneno_ticks > 0:
                self.hp -= self.veneno_dano_por_tick
                self.veneno_ticks -= 1
                self.veneno_proximo_tick = now + self.veneno_intervalo

                # Inicia animação de hit como feedback visual (opcional)
                self.anima_hit = True
                self.time_last_hit_frame = now

            if self.veneno_ticks <= 0:
                self.veneno_ativo = False

    def desenhar(self, tela, player_pos):
        clock = time.Clock()
        if self.anima_hit:
            frame = self.frames_hit[self.frame_hit_index]
        elif self.frames:
            frame = self.frames[self.frame_index]
        else:
            corpo = Rect(self.x, self.y, self.largura, self.altura)
            draw.rect(tela, (255, 0, 0), corpo)
            frame = None

        if frame:
            tela.blit(frame, (self.x, self.y))

        # vida
        draw.rect(tela, (255, 200, 200), (self.x - 20, self.y + 70, 100, 10))
        draw.rect(tela, (255, 0, 0), (self.x - 20, self.y + 70, self.hp, 10))

        rot_rect, rot_surf = self.get_hitbox_ataque(player_pos)
        tela.blit(rot_surf, rot_rect)

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 500:
            if getattr(self, 'ultimo_dano_critico', False):
                cor = (255, 215, 0)  # Amarelo-ouro
                tamanho_fonte = 24  # Texto maior
                offset_extra = 5 * math.sin(time.get_ticks() / 50)
                texto = "!"
            else:
                cor = (255, 50, 50)
                tamanho_fonte = 20
                offset_extra = 0
                texto = ""

            fonte_atual = font.Font('assets/Fontes/alagard.ttf', tamanho_fonte)
            dano_text = fonte_atual.render(f"{self.ultimo_dano:.1f}{texto}", True, cor)

            sombra = fonte_atual.render(f"{self.ultimo_dano:.1f}{texto}", True, (0, 0, 0))

            offset_y = (time.get_ticks() - self.ultimo_dano_tempo) / 4
            pos_x = self.x + self.largura / 2 - dano_text.get_width() / 2
            pos_y = self.y - 5 - offset_y + offset_extra

            tela.blit(sombra, (pos_x + 2, pos_y + 2))
            tela.blit(dano_text, (pos_x, pos_y))




    def get_hitbox_ataque(self, player_pos):
        if not hasattr(self, '_last_angle') or self._last_pos != player_pos:
            player_x, player_y = player_pos
            dx = (player_x + 32) - (self.x + 32)
            dy = (player_y + 32) - (self.y + 32)
            self._last_angle = math.atan2(dy, dx)
            self._last_pos = player_pos

        # player_x = player_pos[0]
        # player_y = player_pos[1]

        # inimigo orbital
        # dx = (player_x+32) - (self.x+32)
        # dy = (player_y+32) - (self.y+32)

        angulo = self._last_angle

        orb_x = self.x + 32 + math.cos(angulo) * (self.radius + 15)
        orb_y = self.y + 32 + math.sin(angulo) * (self.radius + 15)

        Orb_rect = Rect(0, 0, *(self.orbital_size))
        Orb_rect.center = (orb_x, orb_y)

        # esse daqui é a hitbox do ataque do inimigo
        orb_surf = Surface(self.hitboxArma, SRCALPHA)
        draw.rect(orb_surf, (255, 0, 0), orb_surf.get_rect(),
                  width=1)  # quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_surf = transform.rotate(orb_surf, -math.degrees(
            angulo))  # quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_rect = rot_surf.get_rect(
            center=Orb_rect.center)  # quadrado sem preenchimento vermelho   que fica com o inimigo

        # tela.blit(rot_surf, Rot_rect) #quadrado sem preenchimento vermelho   que fica com o inimigo

        return rot_rect, rot_surf

    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)





