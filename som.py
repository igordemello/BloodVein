from pygame import *
from pygame import mixer
import time
from threading import Thread

mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
class GerenciadorDeSom:
    def __init__(self, volume=0.1, max_channels=32):
        mixer.set_num_channels(max_channels)
        self.volume = volume
        self.max_channels = max_channels
        self.sons = {}
        self.canais_ocupados = {}

        # Carrega os sons em uma thread separada para não travar o jogo
        self.carregar_sons_thread = Thread(target=self._carregar_sons, daemon=True)
        self.carregar_sons_thread.start()

    def _carregar_sons(self):
        sons_para_carregar = {
            "hover": "sons/hover.mp3",
            "buy": "sons/compra.mp3",
            "martelo2": "sons/AOEMartelo.mp3",
            "arco": "sons/Arco.mp3",
            "arco_acerto": "sons/ArcoAcerto.mp3",
            "click2": "sons/Click2.mp3",
            "click3": "sons/Click2.mp3",
            "Dano1": "sons/Dano1.mp3",
            "Dano2": "sons/Dano2.mp3",
            "Dano3": "sons/Dano3.mp3",
            "dash": "sons/dash.mp3",
            "espada1": "sons/espada1.mp3",
            "espada2": "sons/espada2.mp3",
            "espada3": "sons/espada3.mp3",
            "faca1": "sons/Faca1.mp3",
            "faca2": "sons/Faca2.mp3",
            "Inimigomorre": "sons/InimigoMorrendo.mp3",
            "Inimigomorre2": "sons/InimigoMorrendo2.mp3",
            "Martelo": "sons/Martelo.mp3",
            "passar_porta": "sons/PassarPorta.mp3",
            "Spawn": "sons/Spawn.mp3",
            "Startar": "sons/StartNewRun.mp3",
            "tripleshota": "sons/TripleShot.mp3",
            "carrega_critico": "sons/CarrendoCriticoEspadaDoTita.mp3",
        }

        for nome, caminho in sons_para_carregar.items():
            try:
                som = mixer.Sound(caminho)
                som.set_volume(self.volume)
                self.sons[nome] = som
            except Exception as e:
                print(f"Erro ao carregar som {nome}: {e}")

    def tocar(self, nome, volume=None, loops=0, fade_ms=0):
        """Toca um som com opções de volume, loops e fade-in"""
        if nome not in self.sons:
            return None

        canal = mixer.find_channel()
        if canal is None:
            canal = self._obter_canal_mais_antigo()
            if canal is None:
                return None

        # Configura o volume - garante que não ultrapasse o volume global
        target_volume = self.volume if volume is None else min(volume, self.volume)
        canal.set_volume(target_volume)

        # Toca o som
        canal.play(self.sons[nome], loops, fade_ms=fade_ms)

        self.canais_ocupados[id(canal)] = {
            "canal": canal,
            "inicio": time.time(),
            "nome": nome,
            "volume": target_volume  # Armazena o volume configurado
        }

        return canal

    def _obter_canal_mais_antigo(self):
        if not self.canais_ocupados:
            return None

        id_mais_antigo = min(self.canais_ocupados.keys(),
                             key=lambda k: self.canais_ocupados[k]["inicio"])
        canal = self.canais_ocupados.pop(id_mais_antigo)["canal"]
        canal.stop()
        return canal

    def parar_todos_sons(self, fade_ms=0):
        """Para todos os sons com fade-out opcional"""
        for canal_info in list(self.canais_ocupados.values()):
            canal_info["canal"].fadeout(fade_ms)
        self.canais_ocupados.clear()

    def set_volume(self, volume):
        """Define o volume global para todos os sons"""
        self.volume = max(0.0, min(volume, 1.0))
        for som in self.sons.values():
            som.set_volume(self.volume)
        for canal_info in self.canais_ocupados.values():
            canal_info["canal"].set_volume(self.volume)

    def atualizar(self):
        """Limpa canais que terminaram de tocar"""
        for canal_id in list(self.canais_ocupados.keys()):
            if not self.canais_ocupados[canal_id]["canal"].get_busy():
                self.canais_ocupados.pop(canal_id)


som = GerenciadorDeSom(volume=0.3)


class GerenciadorDeMusica:
    def __init__(self, volume=0.5, fade_duration=1000):
        self.volume = volume
        self.fade_duration = fade_duration  # ms para transições
        self.musica_atual = None
        self.proxima_musica = None
        self.musica_fade_out = False
        self.musica_fade_in = False
        self.fade_start_time = 0
        mixer.music.set_volume(self.volume)

    def tocar(self, caminho, loop=-1, fade_ms=None):
        """Toca música com transição suave"""
        if fade_ms is None:
            fade_ms = self.fade_duration

        if self.musica_atual == caminho and mixer.music.get_busy():
            return

        # Se já está tocando música, faz fade out antes de trocar
        if mixer.music.get_busy() and fade_ms > 0:
            self.proxima_musica = (caminho, loop)
            self.musica_fade_out = True
            self.fade_start_time = time.time()
            mixer.music.fadeout(fade_ms)
        else:
            self._tocar_musica_diretamente(caminho, loop)

    def _tocar_musica_diretamente(self, caminho, loop):
        try:
            mixer.music.load(caminho)
            mixer.music.play(loop)
            self.musica_atual = caminho
            self.proxima_musica = None
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

    def atualizar(self):
        """Atualiza as transições de música"""
        if self.musica_fade_out and not mixer.music.get_busy():
            self.musica_fade_out = False
            if self.proxima_musica:
                caminho, loop = self.proxima_musica
                self._tocar_musica_diretamente(caminho, loop)
                mixer.music.set_volume(0)
                self.musica_fade_in = True
                self.fade_start_time = time.time()

        if self.musica_fade_in:
            progresso = (time.time() - self.fade_start_time) * 1000 / self.fade_duration
            if progresso >= 1.0:
                mixer.music.set_volume(self.volume)
                self.musica_fade_in = False
            else:
                mixer.music.set_volume(self.volume * progresso)

        # Garante que o volume dos efeitos sonoros não seja alterado
        som.set_volume(som.volume)

    def pausar(self):
        """Pausa a música atual"""
        mixer.music.pause()

    def retomar(self, fade_ms=None):
        """Retoma a música pausada com fade-in opcional"""
        if fade_ms is None:
            fade_ms = self.fade_duration

        mixer.music.unpause()
        if fade_ms > 0:
            mixer.music.set_volume(0)
            self.musica_fade_in = True
            self.fade_start_time = time.time()

    def parar(self, fade_ms=None):
        """Para completamente a música com fade-out opcional"""
        if fade_ms is None:
            fade_ms = self.fade_duration

        if fade_ms > 0:
            mixer.music.fadeout(fade_ms)
        else:
            mixer.music.stop()
        self.musica_atual = None

    def set_volume(self, volume, fade_ms=0):
        """Define o volume da música com transição suave"""
        self.volume = max(0.0, min(volume, 1.0))
        if fade_ms > 0:
            # Implementação de fade de volume suave
            pass  # Pode ser implementado com um sistema de atualização gradual
        else:
            mixer.music.set_volume(self.volume)


musica = GerenciadorDeMusica(volume=0.3)