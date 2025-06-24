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
from gerenciador_andar import GerenciadorAndar
from GerenciamentodeTelas import gerenciamento
from menu import Menu


init()

gerenciamento.modo = 'menu'

clock = time.Clock()
SCREEN = display.set_mode((1920, 1080), vsync=1, flags=HWSURFACE | DOUBLEBUF)  # mudei para funcionar em hardware fudido
fps_font = font.SysFont("Arial", 24)
fps_text = fps_font.render("FPS: 60", True, (255, 255, 255))

imagem_cursor = transform.scale(image.load(r'assets\UI\cursor.png').convert_alpha(), (32, 32))
mouse.set_visible(False)

jogo_pausado = False

# Instâncias das classes que foram criadas:
player = Player(950, 600, 32 * 2, 48 * 2)
hud = Hud(player)
andar = GerenciadorAndar("data/andar1.json")
sala_atual = Sala(andar.get_arquivo_atual(), SCREEN, player, andar)
num_sala = 1
fonte = font.SysFont("Arial", 24)
# exemplo de como seria para adicionar um item pro jogador
# player.adicionarItem(conjIt.itens["Sapato de Sangue"])


menu = Menu(SCREEN)
esperar_soltar_clique = True


# while "Fred" == "Fred":
i = 1
while i == 1:
    # i+=1
    keys = key.get_pressed()
    mouse_pos = mouse.get_pos()
    clock.tick(60)
    dt = clock.get_time()
    current_time = time.get_ticks()

    for ev in event.get():
        if ev.type == QUIT:
            quit()
            sys.exit()

        if gerenciamento.modo == 'menu':
            menu.desenho(SCREEN)
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                escolha = menu.checar_clique(mouse_pos)
                if escolha == 'jogo':
                    gerenciamento.modo = "jogo"
                elif escolha == "sair":
                    quit()
                    sys.exit()

        if gerenciamento.modo == 'sair':
            quit()
            sys.exit()

        if gerenciamento.modo == "jogo":
            if esperar_soltar_clique:
                if not mouse.get_pressed()[0]:
                    esperar_soltar_clique = False
            else:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    if jogo_pausado:
                        item = sala_atual.bau.checar_clique_bau(mouse.get_pos())
                        if item:
                            player.adicionarItem(item)
                            jogo_pausado = False
                    else:
                        player.ataque_espada(sala_atual.inimigos, mouse_pos, dt)
                if ev.type == KEYDOWN:
                    if ev.key == K_q and current_time - player.ativo_ultimo_uso > 2500:  # tecla de usar item ativo
                        player.ativo_ultimo_uso = current_time
                        player.usarItemAtivo(sala_atual)

                    if ev.key == K_MINUS:
                        jogo_pausado = not jogo_pausado

                    if ev.key == K_PERIOD:
                        item_id = int(input("Digite o ID do item para debug: "))
                        encontrado = False
                        for item_nome, item in sala_atual.itensDisp.itens.items():
                            if hasattr(item, 'id') and item.id == item_id:
                                if isinstance(item, Item):
                                    player.adicionarItem(item)
                                elif isinstance(item, ItemAtivo):
                                    player.adicionarItem(item)
                                print(f"Item '{item_nome}' (ID {item_id}) adicionado ao jogador.")
                                encontrado = True
                                break

    if gerenciamento.modo == 'jogo':
        SCREEN.blit(imagem_cursor, mouse_pos)
        hud.desenhar(SCREEN)
        sala_atual.desenhar(SCREEN)
        player.desenhar(SCREEN,
                        mouse_pos)  # probleminha, a espada continua sendo atualizado, pq ele é desenhado assim no futuro
        if not jogo_pausado:
            sala_atual.atualizar(dt, keys)
            player.atualizar(dt, keys)
        else:
            sala_atual.bau.bauEscolherItens(SCREEN)


        # mostrar o fps:
        if time.get_ticks() % 500 < 16:  # Atualiza ~30 vezes por segundo
            fps = int(clock.get_fps())
            fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))

        SCREEN.blit(fps_text, (10, 10))

    SCREEN.blit(imagem_cursor, mouse_pos)
    display.update()