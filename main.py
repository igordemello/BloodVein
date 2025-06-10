from pygame import *
import sys
from pygame.locals import QUIT
import math

'''
class Inimigo:
    def __init__(self, ini_x, ini_y):
        self.ini_x = ini_x
        self.ini_y = ini_y
    def hitbox(ini_x,ini_y,pos_x,pos_y):
        inimigoHitbox = Rect(ini_x, ini_y, 200, 200)
        inimigo = Rect(ini_x+75, (ini_y+75), 50, 50) 
        personagem = Rect(pos_x,pos_y,50,50)
'''


clock = time.Clock()


pos_x = 950
hp = 100
pos_y = 600
rate = 1

mapa_joguinho = []

with open("mapa.txt", "r") as file:
    for linha in file:
        linha = linha.rstrip("\n")
        mapa_joguinho.append(linha)


#resolver o tamanho do mapa (desenhar o mapa no ponto a partir da hud, ou seja, y = 184)



tile_size = 32
screen = display.set_mode((1920, 1080))

frame_a = 1
time_frame_a = 0
ini_x = 300
ini_y = 700

radius = 70 #controla a distância da arma pro jogador
angle_offset = 0
orbital_size = (40, 20)
hitboxArma = (70,100)

atacou = False

tiles_solidos = ['G']
tiles_colliders = []

while True:
    for ev in event.get():
        if ev.type == QUIT:
            quit()
            sys.exit()
        if ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                atacou = True

    keys = key.get_pressed()
    #código pra arma
    mouse_x, mouse_y = mouse.get_pos()
    dx = mouse_x - (pos_x + 32)
    dy = mouse_y - (pos_y + 32)
    angle = math.atan2(dy, dx)

    # Orbital preso a uma órbita fixa, apontando na direção do mouse
    orbital_x = pos_x + 32 + math.cos(angle) * radius
    orbital_y = pos_y + 32 + math.sin(angle) * radius
    orbital2_x = pos_x + 32 + math.cos(angle) * (radius+15)
    orbital2_y = pos_y + 32 + math.sin(angle) * (radius+15)

    orbital_rect = Rect(0, 0, *orbital_size)
    orbital_rect.center = (orbital_x, orbital_y)
    orbital_rect2 = Rect(0, 0, *orbital_size)
    orbital_rect2.center = (orbital2_x, orbital2_y)

    #-------------------------------------------------------------------
    antigo_x = pos_x
    antigo_y = pos_y

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
                draw.rect(screen, (120,120,120),((j*32,i*32,32,32)))
            if tile == "W":
                draw.rect(screen,(200,200,200),(j*32,i*32,32,32))



    draw.rect(screen,(0,0,0), (0,0,1920,192))
    vida = draw.rect(screen,(255,5,5), (32,32, 100*(hp/20), 50))


    hp -= 0.05*rate
    #inimigo:
    inimigoHitbox = Rect(ini_x, ini_y, 200, 200)
    inimigo = Rect(ini_x+75, (ini_y+75), 50, 50)


    personagem = Rect(pos_x,pos_y,64,96)
    
    
    # if pos_x not in range(ini_x, ini_x+50):
    #     if pos_x > ini_x+150:
    #         ini_x += 2
    #     elif pos_x < ini_x:
    #         ini_x -= 2
    # if pos_y not in range(ini_y, ini_y+50):
    #     if pos_y > ini_y+150:
    #         ini_y += 2
    #     elif pos_y < ini_y:
    #         ini_y -= 2
    


    inimigoHitbox = draw.rect(screen, (255,0,0),(inimigoHitbox),1)
    inimigo = draw.rect(screen, (255,0,0),(inimigo))
    personagem = draw.rect(screen, (0,255,0),(personagem))

    #arminha denovo
    orbital_surf = Surface(orbital_size, SRCALPHA)
    orbital_surf.fill((0, 0, 255))
    rotated_surf = transform.rotate(orbital_surf, -math.degrees(angle))
    rotated_rect = rotated_surf.get_rect(center=orbital_rect.center)

    #esse daqui é so pra fazer a "hitbox"
    orbital_surf2 = Surface(hitboxArma, SRCALPHA)
    draw.rect(orbital_surf2, (255, 0, 0), orbital_surf2.get_rect(), width=1)  # apenas borda vermelha
    rotated_surf2 = transform.rotate(orbital_surf2, -math.degrees(angle))
    rotated_rect2 = rotated_surf2.get_rect(center=orbital_rect2.center)
    #se usa esse rotated rect2 pra colisão da hitbox da espada
    screen.blit(rotated_surf, rotated_rect)
    screen.blit(rotated_surf2, rotated_rect2)
    #---------------------------------------------------------------------
    if keys[K_d]:
        pos_x = pos_x + 0.3*dt


    if keys[K_a]:
        pos_x = pos_x - 0.3*dt

    if keys[K_w]:
        pos_y = pos_y - 0.3*dt

    if keys[K_s]:
        pos_y = pos_y + 0.3*dt




    coli_pers = Rect(pos_x, pos_y, 64, 96)

    colideInimigo = Rect(ini_x+75, ini_y+75, 50, 50)

    hitboxInimigo = Rect(ini_x, ini_y, 200, 75)
    hitboxInimigo2 = Rect(ini_x, ini_y, 75, 200)
    hitboxInimigo3 = Rect(ini_x+125, ini_y, 75, 200)
    hitboxInimigo4 = Rect(ini_x, ini_y+125, 200, 75)



    #colisão do inimigo
    if coli_pers.colliderect(colideInimigo):
        pos_x = antigo_x
        pos_y = antigo_y

    #colisão com o mapa:
    for collider in tiles_colliders:
        if coli_pers.colliderect(collider):
            pos_x = antigo_x
            pos_y = antigo_y


    #colisão da hitbox
    if coli_pers.colliderect(hitboxInimigo):
        pass
    elif coli_pers.colliderect(hitboxInimigo2):
        pass
    elif coli_pers.colliderect(hitboxInimigo3):
        pass
    elif coli_pers.colliderect(hitboxInimigo4):
        pass

    #algo estranho: de vez em quando ele entende como ataque mesmo nao estando exatamente na hitbox
    if atacou:
        if colideInimigo.colliderect(rotated_rect2):
            print("gg")
            atacou = False



    display.update()
