from pygame import *
import sys
from pygame.locals import QUIT
import math
from pytmx.util_pygame import load_pygame
import pytmx
from gerenciador_andar import GerenciadorAndar
from screen_shake import screen_shaker


class Mapa:
    def __init__(self, caminho_tmx, tela, tela_width, tela_heigth, gerenciador_andar, escala=3):
        # self.tmx_data = load_pygame(f'mapas/{caminho_tmx}')
        self.tmx_data = load_pygame(f'mapas/andar1/teste.tmx')
        self.escala = escala
        self.tela = tela
        self.tela_width = tela_width
        self.tela_heigth = tela_heigth
        self.gerenciador_andar = gerenciador_andar
        self.gid_cache = {}
        
        # Inicializar colisões
        self.colliders = self.get_colliders()
        self.colliders_sem_obstaculo = self.get_colliders_sem_obstaculo()

        # Inicializar o cache do mapa
        self.mapa_cache = None
        self._last_porta_state = None

    def desenhar(self, porta_liberada):
        if self.mapa_cache is None or self._last_porta_state != porta_liberada:
            self._last_porta_state = porta_liberada
            self._recriar_cache(porta_liberada)
        
        offset_x, offset_y = screen_shaker.offset
        rect_mapa = self.mapa_cache.get_rect(center=(
            self.tela_width // 2 + offset_x,
            (self.tela_heigth + 184) // 2 + offset_y
        ))
        self.tela.blit(self.mapa_cache, rect_mapa)

        # Desenhar colisões
        # for col in self.get_colliders():
        #     draw.rect(self.tela, (255, 0, 0), col["rect"], 2)

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

    def get_tile_colliders(self):
        colliders = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if not gid:
                        continue

                    # Pegue o gid original (sem flip) e os flags
                    tiled_gid = self.tmx_data.tiledgidmap.get(gid)
                    flags = None
                    for g, f in self.tmx_data.gidmap[tiled_gid]:
                        if g == gid:
                            flags = f
                            break

                    tile_props = self.tmx_data.get_tile_properties_by_gid(gid)
                    if tile_props and "colliders" in tile_props:
                        for obj in tile_props["colliders"]:
                            if obj.width == 0 or obj.height == 0:
                                continue

                            obj_x = obj.x
                            obj_y = obj.y

                            if flags:
                                if flags.flipped_horizontally:
                                    obj_x = tile_w - obj.width - obj.x
                                if flags.flipped_vertically:
                                    obj_y = tile_h - obj.height - obj.y

                            world_x = (x * tile_w + obj_x) * self.escala + offset_x
                            world_y = (y * tile_h + obj_y) * self.escala + offset_y
                            world_w = obj.width * self.escala
                            world_h = obj.height * self.escala

                            rect = Rect(world_x, world_y, world_w, world_h)
                            tipo = tile_props.get("tipo_colisao", "parede")

                            colliders.append({
                                "rect": rect,
                                "tipo": tipo
                            })

        return colliders


    def _get_object_colliders(self, layer_names):
        colliders = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name in layer_names:
                for obj in layer:
                    if obj.name == 'bau' and not self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'bau':
                        continue
                    rect = Rect(
                        obj.x * self.escala + offset_x,
                        obj.y * self.escala + offset_y,
                        obj.width * self.escala,
                        obj.height * self.escala
                    )
                    colliders.append({"rect": rect})
        return colliders

    def get_colliders(self):
        colliders = []
        for coll in self.get_tile_colliders():
            colliders.append({"rect": coll["rect"]})
        colliders.extend(self._get_object_colliders(["colisor_obstaculo", "colisor_parede"]))
        return colliders

    def get_colliders_sem_obstaculo(self):
        colliders = []
        for coll in self.get_tile_colliders():
            if coll["tipo"] == 'parede':
                colliders.append({"rect": coll["rect"]})
        colliders.extend(self._get_object_colliders(["colisor_parede"]))
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
    
    def get_inimigospawn(self):
        spawn = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "inimigo_spawn":
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        spawn.append(rect.topleft)
        return spawn
    
    def get_rangeloja(self):
        rangeloja = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "range_loja":
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        rangeloja.append(rect)
        return rangeloja
    
    def get_espinhos(self):
        range_espinho = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "range_espinhos":
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        range_espinho.append(rect)
        return range_espinho
    
    def get_trocar_andar(self):
        portal = []
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        largura_total = self.tmx_data.width * tile_w * self.escala
        altura_total = self.tmx_data.height * tile_h * self.escala
        mapa_rect = Rect(0, 0, largura_total, altura_total)
        mapa_rect.center = (self.tela_width // 2, (self.tela_heigth + 184) // 2)
        offset_x, offset_y = mapa_rect.topleft

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "range_trocar_andar":
                    for obj in layer:
                        rect = Rect(
                            obj.x * self.escala + offset_x,
                            obj.y * self.escala + offset_y,
                            obj.width * self.escala,
                            obj.height * self.escala
                        )
                        portal.append(rect)
        return portal

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