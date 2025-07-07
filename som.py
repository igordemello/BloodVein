
from pygame import *
from pygame import mixer

class GerenciadorDeSom:
    def __init__(self, volume=0.5):
        mixer.init()
        self.volume = volume
        self.sons = {
            "hover": mixer.Sound("sons/hover.mp3"),
            "click": mixer.Sound("sons/clicke.mp3"),
            "buy": mixer.Sound("sons/compra.mp3"),
            "ataque1": mixer.Sound("sons/espada1.mp3"),
            "ataque2": mixer.Sound("sons/espada2.mp3"),
            "dash": mixer.Sound("sons/dash.mp3")
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



class GerenciadorDeMusica:
    def __init__(self, volume=0.5):
        mixer.init()
        self.volume = volume
        self.musica_atual = None
        mixer.music.set_volume(self.volume)
        

    def tocar(self, caminho, loop=-1):
        """Toca a música do caminho fornecido. `loop=-1` toca infinitamente."""
        if self.musica_atual != caminho:
            try:
                mixer.music.load(caminho)
                mixer.music.play(loop)
                self.musica_atual = caminho
            except Exception as e:
                print(f"Erro ao carregar música: {e}")

    def pausar(self):
        """Pausa a música atual."""
        mixer.music.pause()

    def retomar(self):
        """Retoma a música pausada."""
        mixer.music.unpause()

    def parar(self):
        """Para completamente a música."""
        mixer.music.stop()
        self.musica_atual = None

    def set_volume(self, volume):
        """Define o volume da música (0.0 a 1.0)."""
        self.volume = max(0.0, min(volume, 1.0))
        mixer.music.set_volume(self.volume)

musica = GerenciadorDeMusica(volume=0.3)
musica_tocando = None

