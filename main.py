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
from efeito import *
from itensDic import *

init()

clock = time.Clock()
SCREEN = display.set_mode((1920, 1080))

#Instâncias das classes que foram criadas:
player = Player(950,600,32*2,48*2)
hud = Hud(player)
sala_atual = Sala("mapas/sala_1.tmx",SCREEN, player)
num_sala = 1
fonte = font.SysFont("Arial", 24)
# instancia o conjunto itens (que possui todos os itens do jogo)
conjIt = ConjuntoItens()

#exemplo de como seria para adicionar um item pro jogador
#player.adicionarItem(conjIt.itens["Sapato de Sangue"])

while (2==2):
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
        num_sala += 1
        sala_atual = Sala(f"mapas/sala_{num_sala}.tmx", SCREEN, player)
        player.x, player.y = 1000, 500
    
    '''
    mostrar o fps:
    fps = int(clock.get_fps())
    texto_fps = fonte.render(f"FPS: {fps}", True, (255, 255, 255))
    SCREEN.blit(texto_fps, (10, 10))
    '''
    display.update()
