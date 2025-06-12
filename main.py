from pygame import *
import sys
from pygame.locals import QUIT
import math
from hud import Hud
from inimigo import Inimigo
from player import Player
from botao import Botao
from mapa import Mapa



clock = time.Clock()
SCREEN = display.set_mode((1920, 1080))





#Instâncias das classes que foram criadas:
inimigoQuad = Inimigo(300,700,64,64)
player = Player(950,600,64,96)
hud = Hud(player)
mapa = Mapa("mapa/mapa.txt")

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

    mapa.desenhar(SCREEN)
    hud.desenhar(SCREEN)

    player.desenhar(SCREEN,mouse_pos)
    player.atualizar(dt,keys)
    
    inimigoQuad.desenhar(SCREEN,(player.x,player.y))
    inimigoQuad.atualizar((player.x,player.y))

    

    #colisão do inimigo
    if player.get_hitbox().colliderect(inimigoQuad.get_hitbox()):
        player.voltar_posicao()
    if inimigoQuad.get_hitbox().colliderect(player.get_hitbox()):
        inimigoQuad.voltar_posicao()
    
        
    #colisão com o mapa:
    for collider in mapa.get_colliders():
        if player.get_hitbox().colliderect(collider):
            player.voltar_posicao()

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
