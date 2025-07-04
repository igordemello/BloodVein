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
from inimigos.MouthOrbBoss import MouthOrb
from sala import Sala
from itensDic import *
from gerenciador_andar import GerenciadorAndar
from menu import Menu
from menu import gerenciamento
from loja import Loja
from minimapa import Minimapa
from menuarmas import *
from screen_shake import screen_shaker
from save_manager import SaveManager
from som import GerenciadorDeSom
from som import som
init()
gerenciamento.modo = 'menu'

clock = time.Clock()
SCREEN = display.set_mode((1920, 1080), vsync=1, flags=HWSURFACE | DOUBLEBUF)
fps_font = font.SysFont("Arial", 24)
fps_text = fps_font.render("FPS: 60", True, (255, 255, 255))

logo = image.load("assets/logo.png")
display.set_icon(logo)
display.set_caption("Blood Vein")

imagem_cursor = transform.scale(image.load(r'assets\UI\cursor.png').convert_alpha(), (32, 32))
mouse.set_visible(False)

jogo_pausado = False

player = Player(950, 600, 32 * 2, 48 * 2)
hud = Hud(player, SCREEN)
andar = GerenciadorAndar("data/andar1.json")
sala_atual = Sala(andar.get_arquivo_atual(), SCREEN, player, andar)
fonte = font.SysFont("Arial", 24)
minimapa = Minimapa(andar, SCREEN)

menu = Menu(SCREEN)
esperar_soltar_clique = True

bau = False
loja = False
menuArmas = True
continuar = False

menuDeArma = MenuArmas(hud)

save_manager = SaveManager()

i = 1
while i == 1:
    keys = key.get_pressed()
    mouse_pos = mouse.get_pos()
    clock.tick(60)
    dt = clock.get_time()
    current_time = time.get_ticks()
    eventos = []

    # Atualiza o screen shake
    screen_shaker.update(dt)

    # FOR DE EVENTOS
    for ev in event.get():
        eventos.append(ev)

        if ev.type == QUIT:
            quit()
            sys.exit()

        # apertando no botão sair do menu
        if gerenciamento.modo == 'sair':
            som.tocar("click")
            quit()
            sys.exit()

        # eventos para se estivermos na tela do menu
        if gerenciamento.modo == 'menu':
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                escolha = menu.checar_clique(mouse_pos)
                if escolha == 'jogo':
                    som.tocar("click")
                    player = Player(950, 600, 32 * 2, 48 * 2)
                    hud = Hud(player, SCREEN)
                    andar = GerenciadorAndar("data/andar1.json")
                    sala_atual = Sala(andar.get_arquivo_atual(), SCREEN, player, andar)
                    minimapa = Minimapa(andar, SCREEN)
                    hud.player = player
                    continuar = False
                    gerenciamento.modo = "jogo"
                elif escolha == "continuar":
                    som.tocar("click")
                    try:
                        loaded_data = save_manager.load_game("save_file.json")

                        player.load_save_data(loaded_data['player'], sala_atual.itensDisp, player.lista_mods)
                        andar.load_save_data(loaded_data['map'])
                        sala_atual = Sala(
                            andar.get_arquivo_atual(), 
                            SCREEN, 
                            player, 
                            andar
                        )
                        sala_atual.load_save_data(loaded_data['sala'], sala_atual.itensDisp)
                        hud = Hud(player, SCREEN)
                        minimapa = Minimapa(andar, SCREEN)
                        hud.player = player
                        continuar = True
                        gerenciamento.modo = "jogo"
                        print("Jogo carregado com sucesso!")
                    except Exception as e:
                        print(f"Erro ao carregar jogo: {e}")
                elif escolha == "sair":
                    quit()
                    sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_DOWN or ev.key == K_s :
                    menu.index_selecionado = (menu.index_selecionado + 1) % len(menu.botoes)
                if ev.key == K_UP or ev.key == K_w:
                    menu.index_selecionado = (menu.index_selecionado - 1) % len(menu.botoes)
                if ev.key == K_RETURN or ev.key == K_SPACE:
                    escolha = menu.botoes[menu.index_selecionado].value
                    if escolha == 'jogo':
                        gerenciamento.modo = "jogo"
                    elif escolha == "sair":
                        quit()
                        sys.exit()

        # eventos para se estivermos na tela do jogo
        if gerenciamento.modo == "jogo":
            if esperar_soltar_clique:
                if not mouse.get_pressed()[0]:
                    esperar_soltar_clique = False
            else:
                if ev.type == MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        if menuArmas and menuDeArma.menu_ativo:
                            resultado = menuDeArma.checar_clique_menu(mouse_pos)
                            if resultado is not None:
                                arma, atributos = resultado
                                player.arma = arma
                                player.atributos = atributos
                                player.atualizar_atributos()

                                if player.arma:
                                    menuArmas = False
                                    hud.atualizar_arma_icon()
                                    player.atualizar_arma()
                                    player.atualizar_atributos()

                        elif sala_atual.bau and sala_atual.ativar_menu_bau:
                            item = sala_atual.bau.checar_clique_bau(mouse.get_pos())
                            if item:
                                player.adicionarItem(item)
                            sala_atual.gerenciador_andar.grafo.nodes[sala_atual.gerenciador_andar.sala_atual]["bau_aberto"] = True
                            sala_atual.bau.menu_ativo = False
                            sala_atual.ativar_menu_bau = False
                            sala_atual.bau_interagido = False
                            sala_atual.player.travado = False
                            jogo_pausado = False

                        elif loja:
                            if sala_atual.loja.checar_compra(mouse.get_pos(), SCREEN) == "sair":
                                 loja = not loja
                        else:
                            player.ataque_espadaPrincipal(sala_atual.inimigos, mouse_pos, dt)
                    if ev.button == 3:
                        player.ataque_espadaSecundario(sala_atual.inimigos, mouse_pos, dt)

                if ev.type == KEYDOWN:
                    if menuArmas:
                        if ev.key == K_RIGHT:
                            menuDeArma.scrollMenu(">")
                            print(menuDeArma.pos)
                        if ev.key == K_LEFT:
                            menuDeArma.scrollMenu("<")
                            print(menuDeArma.pos)

                    if ev.key == K_q and current_time - player.ativo_ultimo_uso > 2500:
                        player.ativo_ultimo_uso = current_time
                        player.usarItemAtivo(sala_atual)

                    if ev.key == K_l:
                        loja = not loja

                    if ev.key == K_o:
                        player.infoArma()

                    if ev.key == K_TAB:
                        minimapa.toggle()

                    if ev.key == K_F5:
                        game_state = save_manager.generate_game_state(player, andar, sala_atual)
                        save_manager.save_game(game_state, "save_file.json")


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

    # aqui ficam os if's para oq acontece dependendo de qual tela estamos

    if gerenciamento.modo == 'menu':
        menu.run()
        menu.desenho(SCREEN)


    if gerenciamento.modo == 'jogo':
        # Limpa a tela
        SCREEN.fill((0, 0, 0))

        # Obtém o offset atual do screen shake
        offset_x, offset_y = screen_shaker.offset

        if not continuar:
            if menuArmas:
                hud.desenhaFundo2()
                menuDeArma.menu_ativo = True
                menuDeArma.menuEscolherItens(SCREEN)
        else:
            hud.desenhaFundo()

            sala_atual.desenhar(SCREEN)  # a própria sala decide se vai mostrar cutscene ou não

            if not (sala_atual.cutscene and sala_atual.cutscene.ativa):
                player.desenhar(SCREEN, mouse_pos)
                hud.desenhar()

            if not jogo_pausado:
                sala_atual.atualizar(dt, keys, eventos)

                if not (sala_atual.cutscene and sala_atual.cutscene.ativa):
                    player.atualizar(dt, keys)

            if sala_atual.bau and sala_atual.bau.menu_ativo:
                sala_atual.bau.bauEscolherItens(SCREEN)
                jogo_pausado = True
            elif loja:
                sala_atual.loja.desenhar_loja(SCREEN)

            hud.update(dt)

            # Mostrar o fps com offset
            if time.get_ticks() % 500 < 16:
                fps = int(clock.get_fps())
                fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
            SCREEN.blit(fps_text, (10 + offset_x, 10 + offset_y))

            minimapa.draw()

    SCREEN.blit(imagem_cursor, (mouse_pos[0], mouse_pos[1] ))
    display.update()