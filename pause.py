from pygame import *
from pygame.math import Vector2
import cv2

class BotaoAnimado:
    def __init__(self, pos, text_input, font, base_color, hovering_color):
        self.pos = pos
        self.text_input = text_input
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.current_color = base_color
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.08
        self.update_text()

    def update_text(self):
        self.text = self.font.render(self.text_input, True, self.current_color)
        self.rect = self.text.get_rect(center=self.pos)

    def changeColor(self, mouse_position):
        if self.rect.collidepoint(mouse_position):
            self.target_scale = 1.1
        else:
            self.target_scale = 1.0

    def update(self, screen):
        # Transição de escala
        self.scale += (self.target_scale - self.scale) * self.scale_speed

        # Transição de cor
        r = self.base_color[0] + (self.hovering_color[0] - self.base_color[0]) * (self.scale - 1) * 10
        g = self.base_color[1] + (self.hovering_color[1] - self.base_color[1]) * (self.scale - 1) * 10
        b = self.base_color[2] + (self.hovering_color[2] - self.base_color[2]) * (self.scale - 1) * 10
        self.current_color = (int(r), int(g), int(b))

        # Atualiza texto com nova cor e aplica escala
        self.update_text()
        scaled_text = transform.rotozoom(self.text, 0, self.scale)
        new_rect = scaled_text.get_rect(center=self.pos)
        screen.blit(scaled_text, new_rect)

    def checkForInput(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Pause:
    def __init__(self):
        self.font = font.Font('assets/Fontes/alagard.ttf', 24)

        # Botões com hover animado
        botao_font = font.Font('assets/Fontes/alagard.ttf', 48)
        cor_base = (228, 133, 40)
        cor_hover = (255, 190, 80)

        self.botaocontinuar = BotaoAnimado((1920//2, 400), "CONTINUAR", botao_font, cor_base, cor_hover)
        self.botaoopcoes = BotaoAnimado((1920//2, 500), "OPÇÕES", botao_font, cor_base, cor_hover)
        self.botaosalvar = BotaoAnimado((1920//2, 600), "SALVAR", botao_font, cor_base, cor_hover)
        self.botaosair = BotaoAnimado((1920//2, 700), "SAIR", botao_font, cor_base, cor_hover)

        self.botoes = [self.botaocontinuar, self.botaoopcoes, self.botaosalvar, self.botaosair]

        self.loop_video = cv2.VideoCapture("assets/UI/pausefundo.mp4")
        self.menu_ativo = False

    def cv2_to_pygame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

    def runPause(self, tela):
        ret, frame = self.loop_video.read()
        if not ret or frame is None:
            self.loop_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.loop_video.read()
        if ret and frame is not None:
            frame = cv2.resize(frame, (1920, 1080))
            pygame_frame = self.cv2_to_pygame(frame)
            tela.blit(pygame_frame, (0, 0))

    def pauseFuncionamento(self, tela):
        self.menu_ativo = True

        # Título
        pause_font = font.Font("assets/Fontes/alagard.ttf", 72)
        pause_text = pause_font.render("PAUSADO", True, (228, 133, 40))
        text_rect = pause_text.get_rect(center=(1920 // 2, 150))
        tela.blit(pause_text, text_rect)

        # Hover e update dos botões
        mouse_pos = mouse.get_pos()
        for botao in self.botoes:
            botao.changeColor(mouse_pos)
            botao.update(tela)

    def checar_clique_pause(self, mouse_pos):
        if not self.menu_ativo:
            return None
        if self.botaocontinuar.checkForInput(mouse_pos):
            self.menu_ativo = False
            return "continuar"
        if self.botaoopcoes.checkForInput(mouse_pos):
            return "opcoes"
        if self.botaosalvar.checkForInput(mouse_pos):
            return "salvar"
        if self.botaosair.checkForInput(mouse_pos):
            return "sair"
        return None
