from pygame import *
import sys
from pygame.locals import QUIT
import math
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
        self.inimigos = [Orb(400,700,64,64)]

        self.colisao = Colisao(self.mapa)
        self.colisao.adicionar_entidade(player)
        for inimigo in self.inimigos:
            self.colisao.adicionar_entidade(inimigo)

        self.porta_liberada = False
        self.player = player
        self.ranges_doors = self.mapa.get_rangesdoors() 

        self.almaspritesheet = image.load('./assets/Itens/almaSpriteSheet.png').convert_alpha()

        self.frames_alma = [self.almaspritesheet.subsurface(Rect(i * 32, 0, 32, 32)) for i in range(4)]

        self.frame_alma_idx = 0
        self.tempo_anterior_alma = time.get_ticks()
        self.duracao_frame_alma = 200

        self.colliders = self.mapa.get_colliders()

        self.gerenciador_andar = gerenciador_andar
        self.proxima_sala = self.gerenciador_andar.ir_para_proxima_sala(0)

    def atualizar(self,dt,teclas):
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.atualizar((self.player.x,self.player.y), self.tela)
                #da o dano no jogador
                inimigo.dar_dano = lambda val=inimigo.dano: self.player.tomar_dano(val)
        
        self.colisao.checar_colisoes(dt)

        if not any(inimigo.vivo for inimigo in self.inimigos):
            self.porta_liberada = True
        
        if self.pode_trocar_de_sala():
             self._trocar_de_sala()

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
        for idx, porta in enumerate(self.ranges_doors):  
            if self.player.get_hitbox().colliderect(porta['colisor']):
                codigo_porta = porta['codigoporta'] 
                nova_sala = self.gerenciador_andar.ir_para_proxima_sala(idx)
                if nova_sala:
                    self.mapa = Mapa(nova_sala, self.tela, self.tela.get_width(), self.tela.get_height())
                    print(f"idx: {idx} - Trocando para: {nova_sala} - codigo porta: {codigo_porta}")

    def desenha_alma(self,pos):
        tempo_atual = time.get_ticks()
        if tempo_atual - self.tempo_anterior_alma >= self.duracao_frame_alma:
            self.tempo_anterior_alma = tempo_atual
            self.frame_alma_idx = (self.frame_alma_idx + 1) % len(self.frames_alma)

        frame = self.frames_alma[self.frame_alma_idx]
        frame = transform.scale(frame, (64, 64))
        rect = frame.get_rect(center=pos)
        self.tela.blit(frame, rect)

