from pygame import *
import sys
from pygame.locals import QUIT
import math
from pytmx.util_pygame import load_pygame
import pytmx
from gerenciador_andar import GerenciadorAndar
from screen_shake import screen_shaker


class Mapa:
    def __init__(self, caminho_tmx, tela, tela_width, tela_heigth,gerenciador_andar, escala=3,):
        self.tmx_data = load_pygame(f'mapas/{caminho_tmx}')
        self.escala = escala
        self.tela = tela
        self.tela_width = tela_width
        self.tela_heigth = tela_heigth
        self.gerenciador_andar = gerenciador_andar
        self.colliders = self.get_colliders()
        self.gid_cache = {}

        # Inicializar o cache do mapa
        self.mapa_cache = None
        self._last_porta_state = None
        self._cache_surface = None




    def desenhar(self, porta_liberada):
        # Verificar se precisa recriar o cache
        if self.mapa_cache is None or self._last_porta_state != porta_liberada:
            self._last_porta_state = porta_liberada
            self._recriar_cache(porta_liberada)
        
        # Usar o cache existente

        offset_x, offset_y = screen_shaker.offset

        rect_mapa = self.mapa_cache.get_rect(center=(
            self.tela_width // 2 + offset_x,
            (self.tela_heigth + 184) // 2 + offset_y
        ))
        self.tela.blit(self.mapa_cache, rect_mapa)


    def _recriar_cache(self, porta_liberada):
        largura = self.tmx_data.width * self.tmx_data.tilewidth * self.escala
        altura = self.tmx_data.height * self.tmx_data.tileheight * self.escala
        self.mapa_cache = Surface((largura, altura), SRCALPHA)

        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight
        
        

        for layer in self.tmx_data:
            if hasattr(layer, "tiles"):
                
                if layer.name.startswith('porta_'):
                    lado = layer.name.removeprefix("porta_").removesuffix("_aberta")

                    portas_sala = self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual].get("portas", {})

                    if lado not in portas_sala:
                        continue

                if layer.name.startswith('porta_'):
                    if not layer.name.endswith("_aberta") and porta_liberada:
                        continue

                     

                for x, y, gid in layer:
                    tile_img = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_img:
                        if gid not in self.gid_cache:
                            scaled_img = transform.scale(tile_img, 
                                                      (tile_w * self.escala, 
                                                       tile_h * self.escala))
                            self.gid_cache[gid] = scaled_img
                            
                        tile_img = self.gid_cache.get(gid)
                        self.mapa_cache.blit(tile_img, 
                                           (x * tile_w * self.escala, 
                                            y * tile_h * self.escala))



    def get_colliders(self):
        colliders = []

        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "colisor_obstaculo" or layer.name == "colisor_parede":
                    for obj in layer:
                        if obj.name == 'bau' and not self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'bau':
                            continue
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )


                        # surface = Surface((rect.width, rect.height), SRCALPHA)
                        # surface.fill((255, 255, 255, 255))  # branco opaco
                        # maska = mask.from_surface(surface)

                        # Guarda rect + mask em forma de dicionário
                        colliders.append({
                            "rect": rect,
                            # "mask": maska
                        })
        return colliders

    def get_rangesdoors(self):
        rangesdoors = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name in self.gerenciador_andar.get_portas_sala(self.gerenciador_andar.sala_atual).keys():
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        rangesdoors.append({'colisor':rect,'codigoporta':layer.name})

        return rangesdoors
    
    def get_rangebau(self):
        rangebau = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == 'range_bau' and self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'bau':
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        rangebau.append(rect)

        print(rangebau)
        return rangebau