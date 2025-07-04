from pygame import *
import sys
from pygame.locals import QUIT
import math
from inimigo import Inimigo
class Orb(Inimigo):
    def __init__(self, x, y, largura, altura, nome="Orb",hp=100,velocidade=2,dano=10):
        super().__init__(x, y, largura, altura, hp,velocidade,dano)
        self.spritesheet = image.load('./assets/Enemies/EyeOrbSprite.png').convert_alpha()
        self.nome = nome
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 16
        self.usar_indices = list(range(0, self.total_frames, 2))
        self.carregar_sprites()

        self.radius = 70
        self.hitbox_arma = (70, 100)
        self.orbital_size = (40, 20)
        self.hitboxArma = (70, 100)

        self.sprite_hit = image.load("assets/Enemies/orbTomandoDano.png").convert_alpha()
        self.frames_hit = []
        self.total_frames_hit = 4
        self.hit_frame_duration = 100
        self.frame_hit_index = 0
        self.time_last_hit_frame = 0
        self.anima_hit = False

        self.carregar_hit_sprites()


    def desenhar(self, tela, player_pos, offset=(0,0)):
        clock = time.Clock()
        offset_x, offset_y = offset

        if self.anima_hit:
            now = time.get_ticks()
            if now - self.time_last_hit_frame > self.hit_frame_duration:
                self.time_last_hit_frame = now
                self.frame_hit_index += 1
                if self.frame_hit_index >= len(self.frames_hit):
                    self.frame_hit_index = 0
                    self.anima_hit = False
                    return

        # Aplica o offset na posição do inimigo
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y

        if self.anima_hit:
            frame = self.frames_hit[self.frame_hit_index]
        elif self.frames:
            frame = self.frames[self.frame_index]
        else:
            corpo = Rect(draw_x, draw_y, self.largura, self.altura)
            draw.rect(tela, (255, 0, 0), corpo)
            frame = None

        if frame:
            tela.blit(frame, (draw_x, draw_y))
            if self.congelado:
                frozen_sprite = frame.copy()
                frozen_sprite.fill((165, 242, 255, 100), special_flags=BLEND_MULT)
                tela.blit(frozen_sprite, (draw_x, draw_y))

        vida_maxima = getattr(self, "hp_max", 100)
        largura_barra = 100
        porcentagem = max(0, min(self.hp / vida_maxima, 1))
        largura_hp = porcentagem * largura_barra

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 2500:
            # Aplica offset na barra de vida
            draw.rect(tela, (255, 200, 200), (draw_x - 20, draw_y + 70, largura_barra, 5))
            draw.rect(tela, (255, 0, 0), (draw_x - 20, draw_y + 70, largura_hp, 5))
            draw.rect(tela, (255, 255, 255), (draw_x - 20, draw_y + 70, largura_barra, 5), 1)

        # Aplica offset na hitbox de ataque
        rot_rect, rot_surf = self.get_hitbox_ataque((player_pos[0] + offset_x, player_pos[1] + offset_y))
        tela.blit(rot_surf, rot_rect)

        if hasattr(self, 'ultimo_dano') and time.get_ticks() - self.ultimo_dano_tempo < 500:
            if getattr(self, 'ultimo_dano_critico', False):
                cor = (255, 215, 0)  # Amarelo-ouro
                tamanho_fonte = 28  # Texto maior
                offset_extra = 5 * math.sin(time.get_ticks() / 50)
                texto = "!"
            else:
                cor = (253, 246, 245)
                tamanho_fonte = 24
                offset_extra = 0
                texto = ""

            fonte_atual = font.Font('assets/Fontes/KiwiSoda.ttf', tamanho_fonte)
            texto_str = f"{self.ultimo_dano:.1f}{texto}"

            offset_y_text = (time.get_ticks() - self.ultimo_dano_tempo) / 4
            pos_x = draw_x + self.largura / 2
            pos_y = draw_y - 5 - offset_y_text + offset_extra

            outline_color = (0, 0, 0)
            outline_size = 1
            for x_offset in [-outline_size, 0, outline_size]:
                for y_offset in [-outline_size, 0, outline_size]:
                    if x_offset == 0 and y_offset == 0:
                        continue  # Pular o centro (preenchimento principal)
                    outline_text = fonte_atual.render(texto_str, True, outline_color)
                    tela.blit(outline_text, (pos_x - outline_text.get_width() / 2 + x_offset,
                                             pos_y + y_offset))

            # Renderizar texto principal
            dano_text = fonte_atual.render(texto_str, True, cor)
            tela.blit(dano_text, (pos_x - dano_text.get_width() / 2, pos_y))

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
        # draw.rect(orb_surf, (255, 0, 0), orb_surf.get_rect(),
        #           width=1)  # quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_surf = transform.rotate(orb_surf, -math.degrees(
            angulo))  # quadrado sem preenchimento vermelho   que fica com o inimigo
        rot_rect = rot_surf.get_rect(
            center=Orb_rect.center)  # quadrado sem preenchimento vermelho   que fica com o inimigo

        # tela.blit(rot_surf, Rot_rect) #quadrado sem preenchimento vermelho   que fica com o inimigo

        return rot_rect, rot_surf
    
    def carregar_hit_sprites(self):
        for i in range(self.total_frames_hit):
            rect = Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = Surface((self.frame_width, self.frame_height), SRCALPHA)
            frame.blit(self.sprite_hit, (0, 0), rect)
            frame = transform.scale(frame, (self.largura, self.altura))
            self.frames_hit.append(frame)