from pygame import *
from pygame.locals import QUIT
import sys
from GerenciamentodeTelas import gerenciamento

class gerenciamento():
    def __init__(self):
        self.modo = "menu"



class Menu():
    def __init__(self, SCREEN):
        self.screen = SCREEN
        self.menuzinho = image.load('assets/UI/Menu_temp.png').convert_alpha()

    def desenho(self,tela):
        tela.blit(self.menuzinho, (0, 0))


    def checar_clique(self, pos):
            x,y = pos
            if 775 <= x <= 1171:
                if 381 <= y < 506:
                    return "jogo"
                elif 881 <= y < 1006:
                    return "sair"