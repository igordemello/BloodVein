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


clock = time.Clock()
SCREEN = display.set_mode((1920, 1080))

#fala galera aqui é o arthur

#Instâncias das classes que foram criadas:
inimigoQuad = Inimigo(400,700,32*2,48*2)
player = Player(950,600,32*2,48*2)
hud = Hud(player)
mapa = Mapa("mapas/mapateste.tmx",SCREEN,SCREEN.get_width(),SCREEN.get_height())
colisao = Colisao(mapa, player, [inimigoQuad])
# i=1
# while i==1:
#     i+=1
while True:  
    for ev in event.get():
        if ev.type == QUIT:
            quit()
            sys.exit()
        if ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                player.atacou = True
        

    keys = key.get_pressed()
    mouse_pos = mouse.get_pos()
    clock.tick(60)
    dt = clock.get_time()
    SCREEN.fill((115,115,115))

    
    hud.desenhar(SCREEN)
    
    mapa.desenhar()
   

    player.desenhar(SCREEN,mouse_pos)
    player.atualizar(dt,keys)
    
    inimigoQuad.desenhar(SCREEN,(player.x,player.y))
    inimigoQuad.atualizar((player.x,player.y))

    colisao.checar_colisoes()
    
    #algo estranho: de vez em quando ele entende como ataque mesmo nao estando exatamente na hitbox
    if player.atacou:
        _, hitbox_espada = player.get_rotated_rect_ataque(mouse_pos)
        if inimigoQuad.get_hitbox().colliderect(hitbox_espada):
            print("gg")
            player.atacou = False
            player.hp += 10
            if player.hp > 100:
                player.hp = 100


    display.update()
