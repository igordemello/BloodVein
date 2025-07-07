
from pygame import *
from pygame import mixer

class GerenciadorDeSom:
    def __init__(self, volume=0.5):
        mixer.init()
        self.volume = volume
        self.sons = {
            "hover": mixer.Sound("sons/hover.mp3"),
            "buy": mixer.Sound("sons/compra.mp3"),
            "martelo2": mixer.Sound("sons/AOEMartelo.mp3"),
            "arco": mixer.Sound("sons/Arco.mp3"),
            "arco_acerto": mixer.Sound("sons/ArcoAcerto.mp3"),
            "click2": mixer.Sound("sons/Click2.mp3"),
            "click3": mixer.Sound("sons/Click2.mp3"),
            "Dano1": mixer.Sound("sons/Dano1.mp3"),
            "Dano2": mixer.Sound("sons/Dano2.mp3"),
            "Dano3": mixer.Sound("sons/Dano3.mp3"),
            "dash": mixer.Sound("sons/dash.mp3"),
            "espada1": mixer.Sound("sons/espada1.mp3"),
            "espada2": mixer.Sound("sons/espada2.mp3"),
            "espada3": mixer.Sound("sons/espada3.mp3"),
            "faca1": mixer.Sound("sons/Faca1.mp3"),
            "faca2": mixer.Sound("sons/Faca2.mp3"),
            "Inimigomorre": mixer.Sound("sons/InimigoMorrendo.mp3"),
            "Inimigomorre2": mixer.Sound("sons/InimigoMorrendo2.mp3"),
            "Martelo": mixer.Sound("sons/Martelo.mp3"),
            "passar_porta": mixer.Sound("sons/PassarPorta.mp3"),
            "Spawn": mixer.Sound("sons/Spawn.mp3"),
            "Startar": mixer.Sound("sons/StartNewRun.mp3"),
            "tripleshota": mixer.Sound("sons/TripleShot.mp3"),
            "carrega_critico": mixer.Sound("sons/CarrendoCriticoEspadaDoTita.mp3"),
            





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

musica = GerenciadorDeMusica(volume=0.1)
musica_tocando = None

