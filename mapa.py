from pygame import *
import sys
from pygame.locals import QUIT
import math
from pytmx.util_pygame import load_pygame
import pytmx


class Mapa:
    def __init__(self, caminho_tmx, tela, tela_width, tela_heigth, escala=3,):
        self.tmx_data = load_pygame(caminho_tmx)
        self.escala = escala
        self.tela = tela
        self.tela_width = tela_width
        self.tela_heigth = tela_heigth

    def desenhar(self):
        largura = self.tmx_data.width * self.tmx_data.tilewidth * self.escala
        altura = self.tmx_data.height * self.tmx_data.tileheight * self.escala
        mapa_surface = Surface((largura, altura), SRCALPHA)

        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile_img in layer.tiles():
                    if tile_img:
                        tile_img = transform.scale(tile_img, (tile_w * self.escala, tile_h * self.escala))
                        mapa_surface.blit(tile_img, (x * tile_w * self.escala, y * tile_h * self.escala))

        rectmapa = mapa_surface.get_rect(center=(self.tela_width // 2, (self.tela_heigth+184) // 2))
        self.tela.blit(mapa_surface, rectmapa)

    def get_colliders(self):
        colliders = []
        tiles_solidos = [1, 3]

        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for y in range(self.tmx_data.height):
                    for x in range(self.tmx_data.width):
                        gid = layer.data[y][x]
                        print(gid)
                        if gid in tiles_solidos:
                            rect = Rect(
                                x * tile_w * self.escala + offset_x,
                                y * tile_h * self.escala + offset_y,
                                tile_w * self.escala,
                                tile_h * self.escala
                            )
                            colliders.append(rect)
        # print(colliders)
        return colliders

