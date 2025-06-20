from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *
from itensDic import ConjuntoItens
from random import sample

class Bau:
    def __init__(self, conjunto : ConjuntoItens):
        self.itensDisp = conjunto
        self.ids_disponiveis = list(conjunto.itens_por_id)
        self.ids_sorteados = sample(self.ids_disponiveis, 3)
        self.itens_sorteados = [self.itensDisp.itens_por_id[id_] for id_ in self.ids_sorteados]

    def bauEscolherItens(self,tela):
        overlay = Surface(tela.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        for pos,itens in enumerate(self.itens_sorteados):
            spriteItem = itens.sprite
            sprite = transform.scale(spriteItem, (128, 128))
            tela.blit(sprite, (650+200*pos, 500))


