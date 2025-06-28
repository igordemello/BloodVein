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

        self.surface.fill((0, 0, 0, 0))
        

        self.draw_bg(self.surface, (0, 0, self.width, self.height), self.color_bg, self.border_radius)
        

        mapa_info = self.gerenciador.get_mapa_info()
        

        for edge in mapa_info['edges']:
            origem_node = next((n for n in mapa_info['nodes'] if n['id'] == edge['origem']), None)
            destino_node = next((n for n in mapa_info['nodes'] if n['id'] == edge['destino']), None)
            
            if origem_node and destino_node and (origem_node['visitada'] or destino_node['visitada']):
                draw.line(
                    self.surface, 
                    self.color_path, 
                    origem_node['posicao'], 
                    destino_node['posicao'], 
                    self.path_width
                )
        

        for node in mapa_info['nodes']:
            should_show = node['visitada'] or (
                'boss' in node['tipo'] and 
                any(edge['origem'] == self.gerenciador.sala_atual and edge['destino'] == node['id'] or
                    edge['destino'] == self.gerenciador.sala_atual and edge['origem'] == node['id']
                    for edge in mapa_info['edges'])
                )

            if not should_show:
                continue
                
            color = (self.color_current if node['atual'] else
                    self.color_spawn if node['tipo'] == 'spawn' else
                    self.color_boss if 'boss' in node['tipo'] else
                    self.color_visited)
                
            room_rect = Rect(
                int(node['posicao'][0]) - self.room_size,
                int(node['posicao'][1]) - self.room_size //2,
                self.room_size*2,
                self.room_size  
            )
            draw.rect(self.surface, color, room_rect)
            
            fonte = font.Font('assets/Fontes/alagard.ttf', 14)
            if node['atual']:
                # text = fonte.render('voce esta aqui', True, self.color_text)
                # text_rect = text.get_rect(center=(node['posicao'][0], node['posicao'][1]))
                # self.surface.blit(text, text_rect)
                icon_resized = transform.scale(self.icon_current, (32,32))
                icon_rect = icon_resized.get_rect()
                icon_rect.center = (node['posicao'][0], node['posicao'][1])
                self.surface.blit(icon_resized, icon_rect)
            elif node['tipo'] == 'spawn':
                # text = fonte.render('spawn', True, self.color_text)
                # text_rect = text.get_rect(center=(node['posicao'][0], node['posicao'][1]))
                # self.surface.blit(text, text_rect)
                icon_resized = transform.scale(self.icon_spawn, (32,32))
                icon_rect = icon_resized.get_rect()
                icon_rect.center = (node['posicao'][0], node['posicao'][1])
                self.surface.blit(icon_resized, icon_rect)
            elif 'boss' in node['tipo']:
                # text = fonte.render('boss', True, self.color_text)
                # text_rect = text.get_rect(center=(node['posicao'][0], node['posicao'][1]))
                # self.surface.blit(text, text_rect)
                icon_resized = transform.scale(self.icon_boss, (32,32))
                icon_rect = icon_resized.get_rect()
                icon_rect.center = (node['posicao'][0], node['posicao'][1])
                self.surface.blit(icon_resized, icon_rect)
            
            
        
        self.screen.blit(self.surface, (self.pos_x, self.pos_y))
        
