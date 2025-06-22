from pygame import *
import sys
from pygame.locals import QUIT
import math

from bau import Bau
from itensDic import ConjuntoItens
from mapa import Mapa
from inimigos.orb import Orb
from colisao import Colisao
import gerenciador_andar

init()
fonte = font.SysFont("Arial", 24)

class Sala:
    def __init__(self, caminho_mapa, tela, player, gerenciador_andar):
        self.tela = tela
        self.mapa = Mapa(caminho_mapa,self.tela,self.tela.get_width(),self.tela.get_height())
        self.gerenciador_andar = gerenciador_andar

        self.colisao = Colisao(self.mapa)
        self.colisao.adicionar_entidade(player)
        

        self.porta_liberada = False
        self.player = player
        self.ranges_doors = self.mapa.get_rangesdoors() 

        self.almaspritesheet = image.load('./assets/Itens/almaSpriteSheet.png').convert_alpha()

        self.frames_alma = [self.almaspritesheet.subsurface(Rect(i * 32, 0, 32, 32)) for i in range(4)]

        self.frame_alma_idx = 0
        self.tempo_anterior_alma = time.get_ticks()
        self.duracao_frame_alma = 200
        self.itensDisp = ConjuntoItens()
        self.colliders = self.mapa.get_colliders()

        self.bau = Bau(self.itensDisp)


        self.em_transicao = False
        self.visitada = False

        
        if not gerenciador_andar.sala_foi_conquistada(gerenciador_andar.sala_atual):
            self.inimigos = self._criar_inimigos()
        else:
            self.inimigos = []
            self.porta_liberada = True
            self.visitada = True

        for inimigo in self.inimigos:
            self.colisao.adicionar_entidade(inimigo)

    def _criar_inimigos(self):
        if "boss" in self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]["tipo"]:
            return [Orb(400, 700, 64, 64, hp=200,velocidade=3, dano=30)]
        else:
            return [Orb(400, 700, 64, 64)]

    def atualizar(self,dt,teclas):
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.atualizar((self.player.x,self.player.y), self.tela)
                #da o dano no jogador
                inimigo.dar_dano = lambda val=inimigo.dano: self.player.tomar_dano(val)
        
        self.colisao.checar_colisoes(dt)

        if not self.visitada:
            self.porta_liberada = False
            if self.player.x > 50 and self.player.x < self.tela.get_width() - 50:
                self.visitada = True
        else:
            self.porta_liberada = not any(inimigo.vivo for inimigo in self.inimigos)
        
        if self.pode_trocar_de_sala() and teclas[K_e]:
             self._trocar_de_sala()
             #self.fade_out()



    def desenhar(self, tela):
        self.mapa.desenhar(self.porta_liberada)
        for inimigo in self.inimigos:
            if inimigo.vivo:
                    inimigo.desenhar(tela, (self.player.x,self.player.y))

            elif not getattr(inimigo, "alma_coletada", True):
                    pos = (inimigo.x+16, inimigo.y+16)

                    self.desenha_alma(pos)
                    alma_hitbox = Rect(0, 0, 50, 50)
                    alma_hitbox.center = pos
                    if self.player.get_hitbox().colliderect(alma_hitbox):
                        self.player.almas += 1
                        inimigo.alma_coletada = True

        
        
        #debug visual das colisões do player e do mapa:
        # for collider in self.mapa.get_colliders():
        #     draw.rect(tela, (255,0,0), collider['rect'], 1)
        # draw.rect(tela, (0,255,0), self.player.player_rect, 2)


    def pode_trocar_de_sala(self):
        return self.porta_liberada and any(self.player.get_hitbox().colliderect(rangee['colisor']) for rangee in self.ranges_doors)


    def _trocar_de_sala(self):
        if self.em_transicao:
            return

        for porta in self.ranges_doors:
            if self.player.get_hitbox().colliderect(porta['colisor']) and self.porta_liberada:
                self.em_transicao = True
                self.fade_out()

                if not any(inimigo.vivo for inimigo in self.inimigos):
                    self.gerenciador_andar.marcar_sala_conquistada(self.gerenciador_andar.sala_atual)

                codigo_porta = porta['codigoporta']

                if f"p{int(codigo_porta[2:])}" in self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]:

                    nova_sala = self.gerenciador_andar.ir_para_proxima_sala(codigo_porta)

                    if nova_sala:
                        nova_instancia = Sala(nova_sala, self.tela, self.player, self.gerenciador_andar)

                        nova_instancia.player = self.player
                        nova_instancia.gerenciador_andar = self.gerenciador_andar
                        nova_instancia.player.player_rect.topleft = (self.tela.get_width() // 2,self.tela.get_height() // 2)

                        self.__dict__.update(nova_instancia.__dict__)

                        self.fade_in() # por algum motivo nao funciona

                        print(f"Transição para: {nova_sala} via {codigo_porta}")
                self.em_transicao = False
                break


    def desenha_alma(self,pos):
        tempo_atual = time.get_ticks()
        if tempo_atual - self.tempo_anterior_alma >= self.duracao_frame_alma:
            self.tempo_anterior_alma = tempo_atual
            self.frame_alma_idx = (self.frame_alma_idx + 1) % len(self.frames_alma)

        frame = self.frames_alma[self.frame_alma_idx]
        frame = transform.scale(frame, (64, 64))
        rect = frame.get_rect(center=pos)
        self.tela.blit(frame, rect)

    def fade_out(self, cor=(0, 0, 0), velocidade=14):
        clock = time.Clock()
        fade = Surface((1472,800))
        fade.fill(cor)
        for alpha in range(0, 255, velocidade):
            fade.set_alpha(alpha)
            self.tela.blit(fade, (224, 248))
            display.update()
            clock.tick(60)

    def fade_in(self, cor=(0, 0, 0), velocidade=14):
        clock = time.Clock()
        fade = Surface((1472,736))
        fade.fill(cor)
        for alpha in range(255, -1, -velocidade):
            fade.set_alpha(alpha)
            self.tela.blit(fade, (224, 248))
            display.update()
            clock.tick(60)

