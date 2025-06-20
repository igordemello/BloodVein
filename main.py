from pygame import *
import sys
from pygame.locals import QUIT
import math

from bau import Bau
from hud import Hud
from inimigo import Inimigo
from player import Player
from botao import Botao
from mapa import Mapa
from colisao import Colisao
from inimigos.orb import Orb
from sala import Sala
from itensDic import *

init()

clock = time.Clock()
SCREEN = display.set_mode((1920, 1080), vsync=1, flags=HWSURFACE | DOUBLEBUF) # mudei para funcionar em hardware fudido
fps_font = font.SysFont("Arial", 24)
fps_text = fps_font.render("FPS: 60", True, (255, 255, 255))

jogo_pausado = False

#Instâncias das classes que foram criadas:
conjunto = ConjuntoItens()
player = Player(950,600,32*2,48*2)
hud = Hud(player)
sala_atual = Sala("mapas/sala_1.tmx",SCREEN, player)
num_sala = 1
fonte = font.SysFont("Arial", 24)
bau = Bau(conjunto)
#exemplo de como seria para adicionar um item pro jogador
#player.adicionarItem(conjIt.itens["Sapato de Sangue"])

# while "Fred" == "Fred":
i = 1
while i == 1:
    # i+=1
    keys = key.get_pressed()
    mouse_pos = mouse.get_pos()
    clock.tick(60)
    dt = clock.get_time()
    SCREEN.fill((115,115,115))
    current_time = time.get_ticks()
    

    for ev in event.get():
        if ev.type == QUIT:
            quit()
            sys.exit()
        if ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                player.ataque_espada(sala_atual.inimigos,mouse_pos,dt)
        if ev.type == KEYDOWN:
            if ev.key == K_q and current_time - player.ativo_ultimo_uso > 2500: #tecla de usar item ativo
                player.ativo_ultimo_uso = current_time
                player.usarItemAtivo(sala_atual)
            if ev.key == K_MINUS:
                jogo_pausado = not jogo_pausado

            if ev.key == K_PERIOD:
                item_id = int(input("Digite o ID do item para debug: "))
                encontrado = False
                for item_nome, item in conjunto.itens.items():
                    if hasattr(item, 'id') and item.id == item_id:
                        if isinstance(item, Item):
                            player.adicionarItem(item=item)
                        elif isinstance(item, ItemAtivo):
                            player.adicionarItem(itemAt=item)
                        print(f"Item '{item_nome}' (ID {item_id}) adicionado ao jogador.")
                        encontrado = True
                        break

    hud.desenhar(SCREEN)
    sala_atual.desenhar(SCREEN)
    player.desenhar(SCREEN, mouse_pos) #probleminha, a espada continua sendo atualizado, pq ele é desenhado assim no futuro
    if not jogo_pausado:
        sala_atual.atualizar(dt, keys)
        player.atualizar(dt,keys)
    else:
        bau.bauEscolherItens(SCREEN)

    #print(player.salaAtivoUsado, '+asdfasdasdasd')
    if sala_atual.pode_trocar_de_sala():
        
        if player.itemAtivo is not None and player.salaAtivoUsado == sala_atual:
 
            if not player.itemAtivo.afetaIni:
                player.itemAtivo.player = player
                player.itemAtivo.remover_efeitos()

        if player.itemAtivoEsgotado is not None:
            if not player.itemAtivoEsgotado.afetaIni:
                player.itemAtivoEsgotado.player = player
                player.itemAtivoEsgotado.remover_efeitos()
            player.itemAtivoEsgotado = None

        num_sala += 1
        sala_atual = Sala(f"mapas/sala_{num_sala}.tmx", SCREEN, player)


        player.x, player.y = 1000, 500

    # mostrar o fps:
    if time.get_ticks() % 500 < 16:  # Atualiza ~30 vezes por segundo
        fps = int(clock.get_fps())
        fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
    
    SCREEN.blit(fps_text, (10, 10))
    display.update()
