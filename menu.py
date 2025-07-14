from pygame import *
from pygame.locals import *
import sys
from botao import Botao
from pygame.math import Vector2
import random
import math
from noise import pnoise2

class gerenciamento():
    def __init__(self):
        self.modo = "menu"

class FogParticle:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.uniform(1.5, 3.5)
        self.speed = random.uniform(0.2, 0.5)
        self.alpha = random.randint(10, 30)
        self.life = random.uniform(0, 2*math.pi)

class FogEffect:
    def __init__(self, width, height, num_particles=400):
        self.width = width
        self.height = height
        self.particles = [FogParticle(width, height) for _ in range(num_particles)]
        self.noise_scale = 0.005
        self.time = 0
        self.speed = 0.05
        self.color = (253, 246, 225)
        self.surface = Surface((width, height), SRCALPHA)
        
    def update(self):
        self.time += self.speed
        
        # Clear the surface
        self.surface.fill((0, 0, 0, 0))
        
        for particle in self.particles:
            # Use Perlin noise for organic movement
            nx = particle.x * self.noise_scale
            ny = particle.y * self.noise_scale + self.time
            noise_val = pnoise2(nx, ny, octaves=1)
            
            # Update position based on noise
            particle.x += math.cos(noise_val * math.pi * 2) * particle.speed
            particle.y += math.sin(noise_val * math.pi * 2) * particle.speed
            
            # Screen wrap-around
            if particle.x < 0: particle.x = self.width
            if particle.x > self.width: particle.x = 0
            if particle.y < 0: particle.y = self.height
            if particle.y > self.height: particle.y = 0
            
            # Gentle pulsing effect
            particle.life += 0.01
            current_alpha = int(particle.alpha * (0.8 + 0.2 * math.sin(particle.life)))
            
            # Draw the particle
            if current_alpha > 5:
                gfxdraw.filled_circle(
                    self.surface,
                    int(particle.x),
                    int(particle.y),
                    int(particle.size),
                    (*self.color, current_alpha))

class Menu():
    def __init__(self, SCREEN):
        self.screen = SCREEN
        self.screen_width, self.screen_height = self.screen.get_size()
        self.fonte = font.Font("assets/Fontes/Alkhemikal.ttf", 180)
        self.fonte_botoes = font.Font("assets/Fontes/alagard.ttf", 72)

        self.cor_base = (253, 246, 225)
        self.cor_hover = (0, 0, 0)

        self.botoes = [
            Botao(None, (600, 420), "Novo Jogo", self.fonte_botoes, self.cor_base, self.cor_hover, "jogo"),
            Botao(None, (600, 520), "Continuar", self.fonte_botoes, self.cor_base, self.cor_hover, "continuar"),
            Botao(None, (600, 620), "Opções", self.fonte_botoes, self.cor_base, self.cor_hover, "opcoes"),
            Botao(None, (600, 720), "Sair", self.fonte_botoes, self.cor_base, self.cor_hover, "sair"),
        ]

        self.hover_escala = [Vector2(1.0, 0.0) for _ in self.botoes]
        self.ultimo_hover = -1

        # Optimized fog effect
        self.fog = FogEffect(self.screen_width, self.screen_height)
        self.last_fog_update = 0

        # Menu assets
        self.menu = image.load("assets/UI/LUA E FUNDO SEM FOG.png").convert_alpha()
        self.index_selecionado = 0
        self.espada_img = image.load("assets/UI/Espada menu.png").convert_alpha()
        self.espada_img = transform.scale(self.espada_img, (100, 50))

    def desenho(self, tela):
        # Draw static background
        tela.blit(self.menu, (0,0))
        
        # Update fog effect only every 2 frames
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fog_update > 50:  # Update every 50ms (~20 FPS)
            self.fog.update()
            self.last_fog_update = current_time
        
        tela.blit(self.fog.surface, (0, 0))
        
        # Play menu music
        musica.tocar("BloodVein SCORE/OST/MainMenuTheme.mp3")
        
        # Draw title with shadow
        titulo_sombra = self.fonte.render("Blood Vein", True, (30, 30, 30))
        tela.blit(titulo_sombra, (200 + 4, 100 + 4))

        titulo = self.fonte.render("Blood Vein", True, (253, 246, 225))
        tela.blit(titulo, (200, 100))

        # Draw buttons
        mouse_pos = mouse.get_pos()
        for i, botao in enumerate(self.botoes):
            is_hovered = botao.rect.collidepoint(mouse_pos) or i == self.index_selecionado

            if is_hovered and i != self.ultimo_hover:
                som.tocar("hover")
                self.ultimo_hover = i
                self.index_selecionado = i

            alvo = Vector2(1.1, -5) if is_hovered else Vector2(1.0, 0.0)
            self.hover_escala[i] = self.hover_escala[i].lerp(alvo, 0.1)

            scale = self.hover_escala[i].x
            offset_y = self.hover_escala[i].y

            cor = botao.hovering_color if is_hovered else botao.base_color
            texto = botao.font.render(botao.text_input, True, cor)
            texto = transform.scale(texto, 
                                 (int(texto.get_width() * scale), 
                                  int(texto.get_height() * scale)))

            sombra = botao.font.render(botao.text_input, True, (50, 50, 50))
            sombra = transform.scale(sombra, 
                                   (int(sombra.get_width() * scale), 
                                    int(sombra.get_height() * scale)))

            pos_x = botao.x_pos - texto.get_width() // 2
            pos_y = botao.y_pos - texto.get_height() // 2 + int(offset_y)

            tela.blit(sombra, (pos_x + 3, pos_y + 3))
            tela.blit(texto, (pos_x, pos_y))

            if i == self.index_selecionado:
                espada_x = pos_x - self.espada_img.get_width() - 20
                espada_y = pos_y + (texto.get_height() // 2) - (self.espada_img.get_height() // 2)
                tela.blit(self.espada_img, (espada_x, espada_y))

    def checar_clique(self, pos):
        for botao in self.botoes:
            if botao.checkForInput(pos):
                return botao.value
        return None