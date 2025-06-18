from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *
import time as t
from sala import *



class Player():
    def __init__(self, x, y, largura, altura, hp=100, st=100,velocidadeMov=0.3,sprite='hero.png'):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

        self.ultimo_uso = 0
        #atributos
        self.hp = hp
        self.hpMax = 100 #atualmente não funciona muito bem quando aumentado porque o sprite não mostra nada acima de 100 de HP
        self.velocidadeMov = velocidadeMov
        self.rate = 1 #decaimento
        self.dano = 20
        self.velocidadeAtk = 1 #analisar esses valores depois com mais cuidado, depois da animação estar pronta, pq vai afetar a velocidade e a duração da animação
        self.revives = 0 #quantidade de vezes que o jogador pode reviver
        self.custoDash = 3.5

        #itens
        
        self.itens = {}
        self.itemAtivo = None
        self.salaAtivoUsado = None

        self.st = st #stamina
        self.cooldown_st = 5000

        self.old_x = x
        self.old_y = y

        self.radius = 70
        self.orbital_size = (40, 20)
        self.hitbox_arma = (70, 100)

        self.atacou = False

        #controles para o dash
        self.dash_cooldown = 0  
        self.dash_duration = 0  
        self.dash_cooldown_max = 1000 
        self.dash_duration_max = 150  
        self.is_dashing = False 
        self.last_dash_time = 0

        self.parado_desde = 0

        self.ativo_ultimo_uso = 0

        self.sprite = transform.scale(image.load(sprite).convert_alpha(),(32*2,48*2))
        self.sword = transform.scale(image.load('assets/Player/Sword_Attack.png').convert_alpha(),(320*2,54*2))

        clock = time.Clock()
        self.dt = clock.get_time()
        self.frame_sword = 0
        self.time_frame_sword = 0
        self.sword_frame_duration = 50
        self.total_frames_espada = 5
        self.anima_espada = False

        self.player_img = self.sprite
        self.player_rect = self.player_img.get_rect(topleft=(self.x,self.y))
        # self.player_mask = mask.from_surface(self.player_img)
        self.dx = 0
        self.dy = 0
        

        

    def _dash(self, dt, teclas, direcao):
        current_time = time.get_ticks()

        if (current_time - self.last_dash_time > self.dash_cooldown_max and 
            not self.is_dashing and teclas[K_SPACE] and self.st >=self.custoDash):
            
            self.last_dash_time = current_time
            self.is_dashing = True
            self.dash_duration = 0

        if self.is_dashing:
            if self.st < self.custoDash:
                self.is_dashing = False
                return

            oldv = self.velocidadeMov
            self.velocidadeMov = self.velocidadeMov*2.5 #velocidadeMov do dash
            if direcao == 'd': self.x += self.velocidadeMov * dt
            elif direcao == 'a': self.x -= self.velocidadeMov * dt
            elif direcao == 'w': self.y -= self.velocidadeMov * dt
            elif direcao == 's': self.y += self.velocidadeMov * dt
            self.velocidadeMov = oldv
            

            self.dash_duration += dt
            if self.dash_duration >= self.dash_duration_max:
                self.is_dashing = False

            self.st -= self.custoDash
        self.ultimo_uso = current_time

    def usarItemAtivo(self, sala_atual : Sala):
        if isinstance(self.itemAtivo, ItemAtivo):
            if self.itemAtivo.afetaIni:
                self.itemAtivo.listaInimigos = sala_atual.inimigos
            else:
                self.itemAtivo.player = self
            self.itemAtivo.aplicar_em()
            self.itemAtivo.usos -= 1
            if self.itemAtivo.usos == 0:
                self.itemAtivo = None
        else:
            print("Não tem item ativo")


    def atualizar(self, dt, teclas):
        self.dt = dt

        current_time = time.get_ticks()
        # cooldown = 2500

        # if teclas[K_w] or teclas[K_a] or teclas[K_s] or teclas[K_d]:
        #     self.parado_desde = current_time  # reseta o tempo parado
        # else:
        #     if current_time - self.parado_desde >= cooldown:
        #         self.st += 0.4 * dt  # começa a recuperar

        self.old_x = self.x
        self.old_y = self.y

        self.x,self.y = self.player_rect.topleft

        # if teclas[K_d]:
        #     self.x += self.velocidadeMov * dt
        #     self._dash(dt, teclas, 'd')
        # if teclas[K_a]:
        #     self.x -= self.velocidadeMov * dt
        #     self._dash(dt, teclas, 'a')
        # if teclas[K_w]:
        #     self.y -= self.velocidadeMov * dt
        #     self._dash(dt, teclas, 'w')
        # if teclas[K_s]:
        #     self.y += self.velocidadeMov * dt
        #     self._dash(dt, teclas, 's')




        self.hp -= 0.05 * self.rate
        
        if current_time - self.last_dash_time >= self.cooldown_st:
            self.st += 0.7 * self.rate

        if self.hp < 0:
            self.hp = 0
        if self.st < 0:
            self.st = 0
        if self.st > 100:
            self.st = 100

        self.atualizar_animacao_espada(dt)

    #tem que fazer uma possibilidade de pegar o item mais de uma vez e ficar incrementando
    def adicionarItem(self,item : Item = None, itemAt : ItemAtivo = None) :
        if item is not None:
            item.aplicar_em(self)
            if item not in self.itens : #tentar entender essa merda que o fred fez depois
                self.itens[item] = 1
            else:
                pass
        else:
            self.itemAtivo = itemAt


    def atualizar_animacao_espada(self, dt):
        if self.anima_espada:
            self.time_frame_sword += dt
            if self.time_frame_sword > self.sword_frame_duration:
                self.frame_sword += 1
                self.time_frame_sword = 0
                if self.frame_sword >= self.total_frames_espada:
                    self.anima_espada = False
                    self.frame_sword = 0


    def calcular_angulo(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        dx = mouse_x - (self.x + 32)
        dy = mouse_y - (self.y + 32)
        return math.atan2(dy, dx)

    def get_rotated_rect_ataque(self, mouse_pos):
        if not hasattr(self, '_last_sword_angle') or self._last_mouse_pos != mouse_pos:
            self._last_sword_angle = self.calcular_angulo(mouse_pos)
            self._last_mouse_pos = mouse_pos
        angle = self._last_sword_angle


        orbital2_x = self.x + 32 + math.cos(angle) * (self.radius + 15)
        orbital2_y = self.y + 32 + math.sin(angle) * (self.radius + 15)

        orbital_rect2 = Rect(0, 0, *self.orbital_size)
        orbital_rect2.center = (orbital2_x, orbital2_y)

        orbital_surf2 = Surface(self.hitbox_arma, SRCALPHA)
        draw.rect(orbital_surf2, (255, 0, 0), orbital_surf2.get_rect(), width=1)
        rotated_surf2 = transform.rotate(orbital_surf2, -math.degrees(angle))
        rotated_rect2 = rotated_surf2.get_rect(center=orbital_rect2.center)

        return rotated_surf2, rotated_rect2

    def mov_player(self,rect):
        self.player_rect.topleft = rect.topleft

    def desenhar(self, tela, mouse_pos):
        tela.blit(self.sprite,(self.player_rect.topleft))
        
        # corpo = Rect(self.x, self.y, self.largura, self.altura)
        # draw.rect(tela, (0, 255, 0), corpo)

        angle = self.calcular_angulo(mouse_pos)
        centro_jogador = (self.x + 32, self.y + 32)

        base_x =  centro_jogador[0] + math.cos(angle) * self.radius
        base_y = 10 + centro_jogador[1] + math.sin(angle) * self.radius

        angulo_espada = math.degrees(angle) - 270

        espada_rotacionada = transform.rotate(self.sword, -angulo_espada)
        rect_espada = espada_rotacionada.get_rect(center=(base_x, base_y))


        orbital_x = self.x + 32 + math.cos(angle) * self.radius
        orbital_y = self.y + 32 + math.sin(angle) * self.radius

        orbital_rect = Rect(0, 0, *self.orbital_size)
        orbital_rect.center = (orbital_x, orbital_y)

        orbital_surf = Surface(self.orbital_size, SRCALPHA)
        orbital_surf.fill((0, 0, 255))
        rotated_surf = transform.rotate(orbital_surf, -math.degrees(angle))
        rotated_rect = rotated_surf.get_rect(center=orbital_rect.center)

        
        frame_largura = 128
        frame_altura = 108
        sword_frame_rect = Rect(self.frame_sword * frame_largura, 0, frame_largura, frame_altura)

        espada_frame = self.sword.subsurface(sword_frame_rect)
        espada_rotacionada = transform.rotate(espada_frame, -math.degrees(angle) - 90)
        rect_espada = espada_rotacionada.get_rect(center=(base_x, base_y))

        tela.blit(espada_rotacionada, rect_espada)

        if self.anima_espada:
            tela.blit(espada_rotacionada, rect_espada.topleft)



        # Hitbox do ataque
        rotated_surf2, rotated_rect2 = self.get_rotated_rect_ataque(mouse_pos)
        #tela.blit(rotated_surf2, rotated_rect2)



    def get_hitbox(self):
        return Rect(self.x, self.y, self.largura, self.altura)

    def voltar_posicao(self):
        self.x = self.old_x
        self.y = self.old_y


    def ataque_espada(self,inimigos,mouse_pos, dt):
        if not self.anima_espada:
            self.anima_espada = True
            self.frame_sword = 0
            self.time_frame_sword = 0

        self.atacou = True
        self.time_frame_sword += self.dt
        if self.time_frame_sword > 150:
            self.frame_sword += 1
            self.time_frame_sword = 0
        if self.frame_sword >= 5:
            self.frame_sword = 0      


        _, hitbox_espada = self.get_rotated_rect_ataque(mouse_pos)
        for inimigo in inimigos:
            if inimigo.vivo:
                if not inimigo.get_hitbox().colliderect(hitbox_espada):
                    self.atacou = False
                if inimigo.get_hitbox().colliderect(hitbox_espada):
                    t.sleep(0.05)
                    self.atacou = False
                    self.hp += self.dano/2
                    if self.hp > self.hpMax:
                        self.hp = self.hpMax
                    inimigo.hp -= self.dano*inimigo.multDanoRecebido

                    #knockback   
                    dx = inimigo.x - self.x
                    dy = inimigo.y - self.y
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        dx /= dist
                        dy /= dist

                    knockback_strength = 4
                    inimigo.knockback_x = dx * knockback_strength
                    inimigo.knockback_y = dy * knockback_strength
                    inimigo.knockback_time = time.get_ticks()
                                
                   