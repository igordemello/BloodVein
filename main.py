from pygame import *
import sys
from pygame.locals import QUIT
import math
from hud import Hud
from inimigo import Inimigo
from player import Player
from botao import Botao



clock = time.Clock()
SCREEN = display.set_mode((1920, 1080))



mapa_joguinho = []
with open("mapa\mapa.txt", "r") as file:
    for linha in file:
        linha = linha.rstrip("\n")
        mapa_joguinho.append(linha)
tile_size = 32
tiles_solidos = ['G']
tiles_colliders = []

#Instâncias das classes que foram criadas:
inimigoQuad = Inimigo(300,700,64,64)
player = Player(950,600,64,96)
hud = Hud(player)

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

    tiles_colliders.clear()
    for i in range(len(mapa_joguinho)):
        for j in range(len(mapa_joguinho[i])):
            tile = mapa_joguinho[i][j]
            if tile in tiles_solidos:
                tile_rect = Rect(j*32,i*32,32,32)
                tiles_colliders.append(tile_rect)
            if tile == "G":
                draw.rect(SCREEN, (120,120,120),((j*32,i*32,32,32)))
            if tile == "W":
                draw.rect(SCREEN,(200,200,200),(j*32,i*32,32,32))


    player.desenhar(SCREEN,mouse_pos)
    player.atualizar(dt,keys)
    
    inimigoQuad.desenhar(SCREEN,(player.x,player.y))
    inimigoQuad.atualizar((player.x,player.y))

    hud.desenhar(SCREEN)

    #colisão do inimigo
    if player.get_hitbox().colliderect(inimigoQuad.get_hitbox()):
        player.voltar_posicao()
    if inimigoQuad.get_hitbox().colliderect(player.get_hitbox()):
        inimigoQuad.voltar_posicao()
    
        
    #colisão com o mapa:
    for collider in tiles_colliders:
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
