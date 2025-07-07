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
from pause import Pause
import os
from gameover import GameOver
import shutil
from som import GerenciadorDeMusica
from som import musica
from inventario import Inventario

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
pause = Pause()
inventarioexibe = False

mensagem_salvo = None
tempo_mensagem_salvo = 0


player = Player(950, 600, 32 * 2, 48 * 2)
hud = Hud(player, SCREEN)
andar = GerenciadorAndar()

fonte = font.Font("assets/fontes/alagard.ttf", 48)

minimapa = Minimapa(andar, SCREEN)

def set_minimapa(novo_minimapa):
    global minimapa
    minimapa = novo_minimapa
sala_atual = Sala(andar.get_arquivo_atual(), SCREEN, player, andar, set_minimapa)
menu = Menu(SCREEN)
esperar_soltar_clique = True

bau = False
loja = False
menuArmas = False
continuar = False
pausado = False

gameOver = GameOver()

menuDeArma = MenuArmas(hud)

save_manager = SaveManager()

inventario = Inventario(SCREEN, player, hud)

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
            som.tocar("click3")
            quit()
            sys.exit()

        # eventos para se estivermos na tela do menu
        if gerenciamento.modo == 'menu':
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                escolha = menu.checar_clique(mouse_pos)
                if escolha == 'jogo':
                    try:
                        os.remove('save_file.json')
                    except (FileNotFoundError, ValueError):
                        print('não existe save para ser apagado')

                    for item in os.listdir('data'):
                        caminho_completo_do_item = os.path.join('data', item)
                        try:
                            os.remove(caminho_completo_do_item)
                        except (FileNotFoundError, ValueError):
                            print('não existe data para ser apagado')
                    som.tocar("Startar")
                    player = Player(950, 600, 32 * 2, 48 * 2)
                    hud = Hud(player, SCREEN)
                    andar = GerenciadorAndar()
                    sala_atual = Sala(f'andar1/spawn.tmx', SCREEN, player, andar, set_minimapa)
                    set_minimapa(Minimapa(andar,SCREEN))
                    hud.player = player
                    inventario = Inventario(SCREEN, player, hud)
                    menuArmas = True
                    continuar = False
                    

                    gerenciamento.modo = "jogo"
                elif escolha == "continuar":
                    som.tocar("click3")
                    try:
                        loaded_data = save_manager.load_game("save_file.json")

                        player.load_save_data(loaded_data['player'], sala_atual.itensDisp, player.lista_mods)
                        andar.load_save_data(loaded_data['map'])
                        sala_atual = Sala(
                            andar.get_arquivo_atual(), 
                            SCREEN, 
                            player, 
                            andar,
                            set_minimapa
                        )
                        sala_atual.load_save_data(loaded_data['sala'], sala_atual.itensDisp)
                        hud = Hud(player, SCREEN)
                        minimapa = Minimapa(andar, SCREEN)
                        hud.player = player
                        continuar = True
                        menuArmas = False
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
                        som.tocar('clicke3')
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
                                arma, atributos, trait = resultado
                                player.arma = arma
                                player.atributos = atributos
                                player.atualizar_atributos()

                                if player.arma:
                                    som.tocar('clique3')
                                    menuArmas = False
                                    hud.atualizar_arma_icon()
                                    player.atualizar_arma()
                                    player.atualizar_atributos()
                                    player.atualizar_traits(trait)

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
                        elif jogo_pausado and pause.menu_ativo:
                            if pause.checar_clique_pause(mouse_pos) == "continuar":
                                pausado = not pausado
                                jogo_pausado = not jogo_pausado
                            elif pause.checar_clique_pause(mouse_pos) == "sair":
                                gerenciamento.modo = "menu"
                                jogo_pausado = not jogo_pausado
                            elif pause.checar_clique_pause(mouse_pos) == "salvar":
                                game_state = save_manager.generate_game_state(player, andar, sala_atual)
                                save_manager.save_game(game_state, "save_file.json")
                                mensagem_salvo = fonte.render("JOGO SALVO", True, (255, 255, 255))
                                tempo_mensagem_salvo = time.get_ticks()
                        elif jogo_pausado and player.gameOver:
                            if gameOver.checar_clique_pause(mouse_pos) == "nova run":
                                try:
                                    os.remove('save_file.json')
                                except (FileNotFoundError, ValueError):
                                    print('não existe save para ser apagado')

                                for item in os.listdir('data'):
                                    caminho_completo_do_item = os.path.join('data', item)
                                    try:
                                        os.remove(caminho_completo_do_item)
                                    except (FileNotFoundError, ValueError):
                                        print('não existe data para ser apagado')
                                som.tocar("click3")
                                player = Player(950, 600, 32 * 2, 48 * 2)
                                hud = Hud(player, SCREEN)
                                andar = GerenciadorAndar()
                                sala_atual = Sala(f'andar1/spawn.tmx', SCREEN, player, andar, set_minimapa)
                                set_minimapa(Minimapa(andar, SCREEN))
                                hud.player = player
                                menuArmas = True
                                menuDeArma.tela_atual = "atributos"
                                jogo_pausado = False
                            elif gameOver.checar_clique_pause(mouse_pos) == "sair":
                                gerenciamento.modo = "menu"
                                jogo_pausado = not jogo_pausado

                        elif inventario.visible:
                            inventario.checar_clique_inventario()
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

                    if ev.key == K_ESCAPE and not inventarioexibe:
                        jogo_pausado = not jogo_pausado
                        pausado = not pausado

                    if ev.key == K_q and current_time - player.ativo_ultimo_uso > 2500:
                        player.ativo_ultimo_uso = current_time
                        player.usarItemAtivo(sala_atual)

                    if ev.key == K_l and not inventarioexibe:
                        loja = not loja

                    if ev.key == K_o:
                        player.infoArma()

                    if ev.key == K_TAB:
                        minimapa.toggle()

                    if ev.key == K_i:
                        pode_abrir = not pausado and not (sala_atual.bau and sala_atual.bau.menu_ativo) and not loja
                        if inventario.visible:
                            inventario.toggle()
                            jogo_pausado = False
                            inventarioexibe = False
                        elif pode_abrir:
                            inventario.toggle()
                            jogo_pausado = True
                            inventarioexibe = True


                    
                        
                        
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

        if menuArmas:
            hud.desenhaFundo2()
            menuDeArma.menu_ativo = True
            menuDeArma.menuEscolherItens(SCREEN)
        else:
            hud.desenhaFundo()
            sala_atual.desenhar(SCREEN)

            if not (sala_atual.cutscene and sala_atual.cutscene.ativa):
                player.desenhar(SCREEN, mouse_pos)
                if inventario.visible:
                    hud.desenhar(minimal=True)
                else:
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
            if jogo_pausado and pausado:
                pause.runPause(SCREEN)
                pause.pauseFuncionamento(SCREEN)
                if mensagem_salvo and time.get_ticks() - tempo_mensagem_salvo < 2000:
                    SCREEN.blit(mensagem_salvo, (1920 // 2 - mensagem_salvo.get_width() // 2, 900))

            if player.gameOver:
                jogo_pausado = True
                gameOver.gameOverFuncionamento(SCREEN)
            minimapa.draw()
            inventario.desenhar()
            
    SCREEN.blit(imagem_cursor, (mouse_pos[0], mouse_pos[1] ))
    display.update()
    