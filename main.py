from pygame import *
import sys
from pygame.locals import QUIT
import math
from hud import Hud
from inimigo import Inimigo
from player import Player
from botao import Botao
from mapa import Mapa
from colisao import Colisao
from inimigos.orb import Orb
from sala import Sala

clock = time.Clock()
SCREEN = display.set_mode((1920, 1080))

#Instâncias das classes que foram criadas:
player = Player(950,600,32*2,48*2)
hud = Hud(player)
mapa = Mapa("mapas/umaporta_1.tmx",SCREEN,SCREEN.get_width(),SCREEN.get_height())
sala_atual = Sala("mapas/umaporta_1.tmx",SCREEN, player)

while True:  

    keys = key.get_pressed()
    mouse_pos = mouse.get_pos()
    clock.tick(60)
    dt = clock.get_time()
    SCREEN.fill((115,115,115))


    for ev in event.get():
        if ev.type == QUIT:
            quit()
            sys.exit()
        if ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                player.ataque_espada(sala_atual.inimigos,mouse_pos)
        

    hud.desenhar(SCREEN)
    
    sala_atual.atualizar(dt, keys)
    sala_atual.desenhar(SCREEN)

    player.desenhar(SCREEN,mouse_pos)
    player.atualizar(dt,keys)

    if sala_atual.pode_trocar_de_sala() and keys[K_e]:
        sala_atual = Sala("mapas/umaporta_2.tmx", SCREEN, player)
        player.x, player.y = 1000, 500


    display.update()
