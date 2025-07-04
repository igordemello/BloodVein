
from pygame import *

class GerenciadorDeSom:
    def __init__(self, volume=0.5):
        mixer.init()
        self.volume = volume
        self.sons = {
            "hover": mixer.Sound("sons/hover.mp3"),
            "click": mixer.Sound("sons/clicke.mp3"),
            "buy": mixer.Sound("sons/compra.mp3"),
            "ataque1": mixer.Sound("sons/espada1.mp3"),
            "ataque2": mixer.Sound("sons/espada2.mp3")
        }

        for som in self.sons.values():
            som.set_volume(self.volume)

    def tocar(self, nome):
        if nome in self.sons:
            self.sons[nome].play()

    def set_volume(self, volume):
        self.volume = volume
        for som in self.sons.values():
            som.set_volume(self.volume)

som = GerenciadorDeSom(volume=0.5)