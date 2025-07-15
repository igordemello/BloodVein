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

from enum import Enum, auto

class EstadoDoJogo(Enum):
    MENU = auto()
    JOGANDO = auto()
    PAUSADO = auto()
    INVENTARIO = auto()
    GAME_OVER = auto()
    ESCOLHA_ARMA = auto()
    LOJA = auto()
    BAU = auto()
    CUTSCENE = auto()

class Game:
    def __init__(self):
        init()
        self.clock = time.Clock()
        self.screen = display.set_mode((1920, 1080), vsync=1, flags=HWSURFACE | DOUBLEBUF)
        display.set_caption("Blood Vein")
        mouse.set_visible(False)
        logo = image.load("assets/logo.png")
        display.set_icon(logo)

        self.imagem_cursor = transform.scale(image.load("assets/UI/cursor.png").convert_alpha(), (32, 32))
        self.imagem_cursor_click = transform.scale(image.load("assets/UI/cursor_click.png").convert_alpha(), (32, 32))
        self.cursor_clicando = False

        self.estado = EstadoDoJogo.MENU
        self.fonte = font.Font("assets/fontes/alagard.ttf", 48)
        self.fps_font = font.SysFont("Arial", 24)
        self.fps_text = self.fps_font.render("FPS: 60", True, (255, 255, 255))

        self.save_manager = SaveManager()
        self.pause = Pause()
        self.game_over = GameOver()
        self.menu = Menu(self.screen)

        

        self.mensagem_salvo = None
        self.tempo_mensagem_salvo = 0

        self.bau_foi_aberto_esse_frame = False

        self.player = None
        self.hud = None
        self.andar = None
        self.minimapa = None
        self.sala_atual = None
        self.menu_armas = None
        self.inventario = None
        self.menu_armas_ativo = None

    def resetar_jogo(self, com_nova_run=False):
        self.player = Player(950, 600, 32 * 2, 48 * 2)
        self.hud = Hud(self.player, self.screen)
        self.andar = GerenciadorAndar()
        self.minimapa = Minimapa(self.andar, self.screen)
        self.sala_atual = Sala("andar1/spawn.tmx", self.screen, self.player, self.andar, self.set_minimapa)
        self.menu_armas = MenuArmas(self.hud)
        self.inventario = Inventario(self.screen, self.player, self.hud)
        self.menu_armas_ativo = com_nova_run

    def set_minimapa(self, novo):
        self.minimapa = novo

    def loop(self):
        while True:
            dt = self.clock.tick(60)
            eventos = event.get()
            mouse_pos = mouse.get_pos()
            keys = key.get_pressed()

            for ev in eventos:
                if ev.type == QUIT:
                    quit()
                    sys.exit()

            screen_shaker.update(dt)
            self.tratar_eventos(eventos, mouse_pos, keys, dt)
            self.atualizar(dt, keys, eventos)
            self.desenhar(mouse_pos)

            if self.cursor_clicando:
                self.screen.blit(self.imagem_cursor_click, mouse_pos)
            else:
                self.screen.blit(self.imagem_cursor, mouse_pos)
            display.update()

    def tratar_eventos(self, eventos, mouse_pos, keys, dt):
        if self.estado == EstadoDoJogo.MENU:
            for ev in eventos:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    escolha = self.menu.checar_clique(mouse_pos)
                    if escolha == "jogo":
                        self.apagar_saves()
                        som.tocar("Startar")
                        self.resetar_jogo(com_nova_run=True)
                        self.estado = EstadoDoJogo.ESCOLHA_ARMA
                    elif escolha == "continuar":
                        som.tocar("click3")
                        try:
                            dados = self.save_manager.load_game("save_file.json")
                            self.resetar_jogo()
                            self.player.load_save_data(dados['player'], self.sala_atual.itensDisp, self.player.lista_mods)
                            self.andar.load_save_data(dados['map'])
                            self.sala_atual = Sala(self.andar.get_arquivo_atual(), self.screen, self.player, self.andar, self.set_minimapa)
                            self.sala_atual.load_save_data(dados['sala'], self.sala_atual.itensDisp)
                            self.estado = EstadoDoJogo.JOGANDO
                        except Exception as e:
                            print(f"Erro ao carregar jogo: {e}")
                    elif escolha == "sair":
                        quit()
                        sys.exit()

        elif self.estado == EstadoDoJogo.JOGANDO:
            for ev in eventos:
                if ev.type == KEYDOWN:
                    if ev.key == K_1: #temporário
                        #self.player.clarao()
                        self.player.bola_de_fogo()
                    if ev.key == K_PERIOD:
                        item_id = int(input("Digite o ID do item para debug: "))
                        encontrado = False
                        for item_nome, item in self.sala_atual.itensDisp.itens.items():
                            if hasattr(item, 'id') and item.id == item_id:
                                if isinstance(item, Item):
                                    self.player.adicionarItem(item)
                                elif isinstance(item, ItemAtivo):
                                    self.player.adicionarItem(item)
                                print(f"Item '{item_nome}' (ID {item_id}) adicionado ao jogador.")
                                encontrado = True
                                break

                    if ev.key == K_ESCAPE:
                        self.estado = EstadoDoJogo.PAUSADO
                    elif ev.key == K_i:
                        self.inventario.toggle()
                        self.estado = EstadoDoJogo.INVENTARIO if self.inventario.visible else EstadoDoJogo.JOGANDO
                    elif ev.key == K_TAB:
                        self.minimapa.toggle()
                    elif ev.key == K_e:
                        if self.sala_atual.hitbox_loja() and self.player.get_hitbox().colliderect(self.sala_atual.hitbox_loja()[0]):
                            self.estado = EstadoDoJogo.LOJA
                elif ev.type == MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        self.player.ataque_espadaPrincipal(self.sala_atual.inimigos, mouse_pos, dt)

                    elif ev.button == 3:
                        self.player.ataque_espadaSecundario(self.sala_atual.inimigos, mouse_pos, dt)

        elif self.estado == EstadoDoJogo.LOJA:
            for ev in eventos:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    resultado = self.sala_atual.loja.checar_compra(mouse_pos, self.screen)
                    if resultado == "sair":
                        self.estado = EstadoDoJogo.JOGANDO

        elif self.estado == EstadoDoJogo.BAU:
            for ev in eventos:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    resultado = self.sala_atual.bau.checar_clique_bau(mouse_pos)

                    if resultado == "sair":
                        self.estado = EstadoDoJogo.JOGANDO
                        self.sala_atual.bau.menu_ativo = False
                        self.sala_atual.ativar_menu_bau = False
                        self.sala_atual.player.travado = False
                    elif resultado:
                        self.player.adicionarItem(resultado)
                        self.sala_atual.gerenciador_andar.grafo.nodes[self.sala_atual.gerenciador_andar.sala_atual]["bau_aberto"] = True
                        self.estado = EstadoDoJogo.JOGANDO
                        self.sala_atual.bau.menu_ativo = False
                        self.sala_atual.ativar_menu_bau = False
                        self.sala_atual.player.travado = False

                    if resultado:
                        self.sala_atual.bau.menu_ativo = False
                        self.sala_atual.ativar_menu_bau = False
                        self.sala_atual.bau_interagido = False
                        self.sala_atual.player.travado = False
                        self.bau_foi_aberto_esse_frame = False

        elif self.estado == EstadoDoJogo.PAUSADO:
            for ev in eventos:
                if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                    self.estado = EstadoDoJogo.JOGANDO
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    escolha = self.pause.checar_clique_pause(mouse_pos)

                    if escolha == "sair":
                        self.estado = EstadoDoJogo.MENU
                        self.pausado = False
                    elif escolha == "continuar":
                        self.estado = EstadoDoJogo.JOGANDO
                        self.pausado = False

        elif self.estado == EstadoDoJogo.INVENTARIO:
            for ev in eventos:
                if ev.type == KEYDOWN and ev.key == K_i:
                    self.inventario.toggle()
                    self.estado = EstadoDoJogo.JOGANDO
            self.inventario.checar_clique_armas(eventos)
            self.inventario.checar_clique_navegacao(eventos)
            self.inventario.checar_clique_inventario(eventos)

        elif self.estado == EstadoDoJogo.GAME_OVER:
            for ev in eventos:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    escolha = self.game_over.checar_clique_pause(mouse_pos)
                    if escolha == "nova run":
                        self.apagar_saves()
                        self.resetar_jogo(com_nova_run=True)
                        self.estado = EstadoDoJogo.ESCOLHA_ARMA
                    elif escolha == "sair":
                        self.estado = EstadoDoJogo.MENU

        elif self.estado == EstadoDoJogo.ESCOLHA_ARMA:
            for ev in eventos:
                if ev.type == KEYDOWN:
                    if ev.key == K_RIGHT:
                        self.menu_armas.scrollMenu(">")
                    elif ev.key == K_LEFT:
                        self.menu_armas.scrollMenu("<")
                elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    resultado = self.menu_armas.checar_clique_menu(mouse_pos)
                    if resultado:
                        arma, atributos, trait = resultado
                        self.player.arma = arma
                        self.player.atributos = atributos
                        self.player.atualizar_arma()
                        self.player.atualizar_atributos()
                        self.player.atualizar_traits(trait)
                        self.hud.atualizar_arma_icon()
                        som.tocar("clique3")
                        self.estado = EstadoDoJogo.JOGANDO

        for ev in eventos:
            if ev.type == MOUSEBUTTONDOWN:
                self.cursor_clicando = True
            elif ev.type == MOUSEBUTTONUP:
                self.cursor_clicando = False

    def atualizar(self, dt, keys, eventos):
        if self.sala_atual:
            if self.sala_atual.cutscene and self.sala_atual.cutscene.ativa:
                self.estado = EstadoDoJogo.CUTSCENE
        if self.estado == EstadoDoJogo.CUTSCENE:
            self.sala_atual.cutscene.update(eventos)
            if not self.sala_atual.cutscene.ativa:
                self.estado = EstadoDoJogo.JOGANDO
            return
        if self.estado == EstadoDoJogo.JOGANDO:
            self.sala_atual.atualizar(dt, keys, eventos)
            self.player.atualizar(dt, keys)
            
            
            if (
                self.estado == EstadoDoJogo.JOGANDO and
                self.sala_atual.bau and
                self.sala_atual.ativar_menu_bau and
                not self.bau_foi_aberto_esse_frame
            ):
                if self.sala_atual.bau.menu_ativo:
                    self.estado = EstadoDoJogo.BAU
                    self.player.travado = True
                    self.bau_foi_aberto_esse_frame = True


            if self.player.gameOver:
                self.apagar_saves()
                self.estado = EstadoDoJogo.GAME_OVER

    def desenhar(self, mouse_pos):
        self.screen.fill((0, 0, 0))
        offset_x, offset_y = screen_shaker.offset

        if self.estado == EstadoDoJogo.MENU:
            self.menu.run()
            self.menu.desenho(self.screen)

        elif self.estado == EstadoDoJogo.ESCOLHA_ARMA:
            self.hud.desenhaFundo2()
            self.menu_armas.menu_ativo = True
            self.menu_armas.menuEscolherItens(self.screen)

        elif self.estado == EstadoDoJogo.JOGANDO:
            self.hud.desenhaFundo()
            self.sala_atual.desenhar(self.screen)
            self.player.desenhar(self.screen, mouse_pos)
            self.sala_atual.desenhar_inimigos(self.screen)
            self.hud.desenhar()
            self.hud.update(self.clock.get_time())
            self.minimapa.draw()
            self.inventario.desenhar()

        elif self.estado == EstadoDoJogo.LOJA:
            self.sala_atual.desenhar(self.screen)
            self.sala_atual.loja.desenhar_loja(self.screen)

        elif self.estado == EstadoDoJogo.BAU:
            self.sala_atual.desenhar(self.screen)
            self.sala_atual.bau.bauEscolherItens(self.screen)

        elif self.estado == EstadoDoJogo.INVENTARIO:
            self.hud.desenhaFundo()
            self.sala_atual.desenhar(self.screen)
            self.player.desenhar(self.screen, mouse_pos)
            self.sala_atual.desenhar_inimigos(self.screen)
            self.hud.desenhar(minimal=True)
            self.hud.update(self.clock.get_time())
            self.minimapa.draw()
            self.inventario.desenhar()


        elif self.estado == EstadoDoJogo.PAUSADO:
            self.pause.runPause(self.screen)
            self.pause.pauseFuncionamento(self.screen)

        elif self.estado == EstadoDoJogo.GAME_OVER:
            self.game_over.gameOverFuncionamento(self.screen)

        elif self.estado == EstadoDoJogo.CUTSCENE:
            self.sala_atual.cutscene.draw(self.screen)

        if time.get_ticks() % 500 < 16:
            fps = int(self.clock.get_fps())
            self.fps_text = self.fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
        self.screen.blit(self.fps_text, (10 + offset_x, 10 + offset_y))

        if self.mensagem_salvo and time.get_ticks() - self.tempo_mensagem_salvo < 2000:
            self.screen.blit(self.mensagem_salvo, (1920 // 2 - self.mensagem_salvo.get_width() // 2, 900))

    def apagar_saves(self):
        try:
            os.remove("save_file.json")
        except:
            pass
        for item in os.listdir("data"):
            try:
                os.remove(os.path.join("data", item))
            except:
                pass
