from pygame import *
from random import randint


class ScreenShake:
    def __init__(self):
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.offset = (0, 0)
        self.active = False

    def start(self, intensity=5, duration=200):
        """Inicia o efeito de screen shake
        Args:
            intensity (float): Intensidade do tremor (2-5 para leve)
            duration (int): Duração do tremor (100-300ms para leve)
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration
        self.active = True

    def update(self, dt):
        """Atualiza o estado do screen shake"""
        if not self.active:
            return

        self.shake_timer -= dt
        if self.shake_timer <= 0:
            self.active = False
            self.offset = (0, 0)
            return

        progress = self.shake_timer / self.shake_duration
        current_intensity = self.shake_intensity * progress * progress  # Suaviza o decaimento

        self.offset = (
            randint(-int(current_intensity), int(current_intensity)),  # Eixo X
            randint(-int(current_intensity), int(current_intensity)))

    def apply(self, original_pos):
        """Retorna a posição com offset aplicado"""
        if not self.active:
            return original_pos
        return (original_pos[0] + self.offset[0],
                original_pos[1] + self.offset[1])


# Instância global
screen_shaker = ScreenShake()