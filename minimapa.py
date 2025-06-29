from pygame import *
import math

class Minimapa:
    def __init__(self, gerenciador_andar, screen):
        self.gerenciador = gerenciador_andar
        self.screen = screen
        self.visible = False
        
        self.width = 700
        self.height = 800
        self.pos_x = (self.screen.get_width() - self.width) // 2 
        self.pos_y = (self.screen.get_height() - self.height) // 2 
        

        self.surface = Surface((self.width, self.height), SRCALPHA)
        

        self.color_bg = (0, 0, 0, 125)
        self.color_visited = (117, 117, 117, 160)
        self.color_current = (117, 117, 117, 160)
        self.color_spawn = (61, 61, 61, 200)
        self.color_boss = (61, 61, 61, 200)
        self.color_path = (150, 150, 150, 160)
        self.color_text = (255, 255, 255, 160)
        

        self.room_size = 50
        self.path_width = 2
        self.border_radius = 20 

        self.icon_current = image.load('assets/minimapa/icon_current.png').convert_alpha()
        self.icon_spawn = image.load('assets/minimapa/icon_spawn.png').convert_alpha()
        self.icon_boss = image.load('assets/minimapa/icon_boss.png').convert_alpha()
        self.icon_bau = image.load('assets/minimapa/icon_bau.png').convert_alpha()


    def toggle(self):
        self.visible = not self.visible

    def draw_bg(self, surface, rect, color, radius=20):
        rect = Rect(rect)
        

        temp = Surface((rect.width, rect.height), SRCALPHA)
        

        draw.rect(temp, color, (radius, 0, rect.width - 2*radius, rect.height),border_radius=radius)


        

        surface.blit(temp, rect.topleft)

    def draw(self):
        if not self.visible:
            return


        mapa_info = self.gerenciador.get_mapa_info()
        
        all_positions = [node['posicao'] for node in mapa_info['nodes']]
        if not all_positions:
            return
        
        min_x = min(pos[0] for pos in all_positions)
        max_x = max(pos[0] for pos in all_positions)
        min_y = min(pos[1] for pos in all_positions)
        max_y = max(pos[1] for pos in all_positions)
        
        content_width = max_x - min_x
        content_height = max_y - min_y
        
        self.width = 700
        self.height = 800
        self.pos_x = (self.screen.get_width() - self.width) // 2
        self.pos_y = (self.screen.get_height() - self.height) // 2
        

        self.surface = Surface((self.width, self.height), SRCALPHA)
        

        self.draw_bg(self.surface, (0, 0, self.width, self.height), self.color_bg, self.border_radius)
        

        scale = min(
            (self.width - 100) / max(content_width, 1), 
            (self.height - 100) / max(content_height, 1)
        )
        
        offset_x = (self.width - content_width * scale) / 2 - min_x * scale
        offset_y = (self.height - content_height * scale) / 2 - min_y * scale
        

        def to_minimap_pos(abs_x, abs_y):
            return (
                int(abs_x * scale + offset_x),
                int(abs_y * scale + offset_y)
            )
        

        for edge in mapa_info['edges']:
            origem_node = next((n for n in mapa_info['nodes'] if n['id'] == edge['origem']), None)
            destino_node = next((n for n in mapa_info['nodes'] if n['id'] == edge['destino']), None)
            
            if origem_node and destino_node and (origem_node['visitada'] or destino_node['visitada']):
                start_pos = to_minimap_pos(*origem_node['posicao'])
                end_pos = to_minimap_pos(*destino_node['posicao'])
                draw.line(
                    self.surface, 
                    self.color_path, 
                    start_pos, 
                    end_pos, 
                    self.path_width
                )
        

        for node in mapa_info['nodes']:
            should_show = node['visitada'] or (
                any(t in node['tipo'] for t in ['boss', 'bau']) and 
                any(edge['origem'] == self.gerenciador.sala_atual and edge['destino'] == node['id'] or
                    edge['destino'] == self.gerenciador.sala_atual and edge['origem'] == node['id']
                    for edge in mapa_info['edges'])
                )

            if not should_show:
                continue
                
            room_pos = to_minimap_pos(*node['posicao'])
            

            scaled_room_size = int(self.room_size * scale * 0.8)
            

            room_rect = Rect(
                room_pos[0] - scaled_room_size,
                room_pos[1] - scaled_room_size // 2,
                scaled_room_size * 2,
                scaled_room_size
            )
            
            color = (self.color_current if node['atual'] else
                    self.color_spawn if node['tipo'] == 'spawn' else
                    self.color_boss if 'boss' in node['tipo'] else
                    self.color_visited)
            
            draw.rect(self.surface, color, room_rect)
            

            icon_size = int(32 * scale * 0.8)
            if node['atual']:
                icon_resized = transform.scale(self.icon_current, (icon_size, icon_size))
                self.surface.blit(icon_resized, (room_pos[0] - icon_size//2, room_pos[1] - icon_size//2))
            elif node['tipo'] == 'spawn':
                icon_resized = transform.scale(self.icon_spawn, (icon_size, icon_size))
                self.surface.blit(icon_resized, (room_pos[0] - icon_size//2, room_pos[1] - icon_size//2))
            elif 'boss' in node['tipo']:
                icon_resized = transform.scale(self.icon_boss, (icon_size, icon_size))
                self.surface.blit(icon_resized, (room_pos[0] - icon_size//2, room_pos[1] - icon_size//2))
            elif 'bau' in node['tipo']:
                icon_resized = transform.scale(self.icon_bau, (icon_size, icon_size))
                self.surface.blit(icon_resized, (room_pos[0] - icon_size//2, room_pos[1] - icon_size//2))
        

        self.screen.blit(self.surface, (self.pos_x, self.pos_y))
        
