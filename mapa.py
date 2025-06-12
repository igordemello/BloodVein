from pygame import *
import sys
from pygame.locals import QUIT
import math


class Mapa:
    def __init__(self, caminho_arquivo, tile_size=32):
        self.tile_size = tile_size
        self.tiles_solidos = ['G']
        self.tiles_colliders = []
        self.mapa = []

        with open(caminho_arquivo, "r") as file:
            for linha in file:
                self.mapa.append(linha.strip())

    def desenhar(self, tela):
        self.tiles_colliders.clear()
        for i in range(len(self.mapa)):
            for j in range(len(self.mapa[i])):
                tile = self.mapa[i][j]
                if tile in self.tiles_solidos:
                    tile_rect = Rect(j*self.tile_size,i*self.tile_size,self.tile_size,self.tile_size)
                    self.tiles_colliders.append(tile_rect)
                if tile == "G":
                    draw.rect(tela, (120,120,120),((j*self.tile_size, i * self.tile_size, self.tile_size, self.tile_size)))
                if tile == "W":
                    draw.rect(tela,(200,200,200),(j*self.tile_size, i * self.tile_size, self.tile_size, self.tile_size))

    def get_colliders(self):
        return self.tiles_colliders