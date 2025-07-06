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
import shutil

class Inventario():
    def __init__(self, screen, player, hud):
        self.screen = screen
        self.visible = False
        self.player = player
        self.hud = hud
        self.fundo = image.load('assets/UI/inventario_fundo.png').convert_alpha()

    def toggle(self):
        self.visible = not self.visible

    def desenhar(self):
        if not self.visible:
            return
        
        self.screen.blit(self.fundo, (0,0))