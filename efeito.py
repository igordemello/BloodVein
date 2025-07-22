from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from abc import ABC, abstractmethod
from inimigo import Inimigo


class Efeito(ABC):
    @abstractmethod
    def aplicar(self, jogador):
        pass

    def remover(self, jogador):
        pass


class AumentarForca(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["forca"]
        jogador.atributos["forca"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        jogador.atributos["forca"] = self.valor_original


class AumentarAgilidade(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["agilidade"]
        jogador.atributos["agilidade"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        jogador.atributos["agilidade"] = self.valor_original


class AumentarDestreza(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["destreza"]
        jogador.atributos["destreza"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        if hasattr(self, 'valor_original'):
            jogador.atributos["destreza"] = self.valor_original


class AumentarVigor(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["vigor"]
        jogador.atributos["vigor"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        if hasattr(self, 'valor_original'):
            jogador.atributos["vigor"] = self.valor_original


class AumentarResistencia(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["resistencia"]
        jogador.atributos["resistencia"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        if hasattr(self, 'valor_original'):
            jogador.atributos["resistencia"] = self.valor_original


class AumentarEstamina(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["estamina"]
        jogador.atributos["estamina"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        if hasattr(self, 'valor_original'):
            jogador.atributos["estamina"] = self.valor_original


class AumentarSorte(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None

    def aplicar(self, jogador):
        self.valor_original = jogador.atributos["sorte"]
        jogador.atributos["sorte"] += self.valor
        jogador.atualizar_atributos()

    def remover(self, jogador):
        if hasattr(self, 'valor_original'):
            jogador.atributos["sorte"] = self.valor_original


class ModificadorDanoRecebido(Efeito):
    def __init__(self, valor):
        self.valor = valor

    def aplicar(self, jogador):
        if isinstance(jogador, Inimigo):
            jogador.modificadorDanoRecebido *= self.valor
            jogador.sangrando = True
        else:
            jogador.base_modificadorDanoRecebido *= self.valor


class DarDano(Efeito):
    def __init__(self, valor):
        self.valor = valor

    def aplicar(self, jogador):
        jogador.hp -= self.valor


class Revives(Efeito):
    def __init__(self, valor):
        self.valor = valor

    def aplicar(self, jogador):
        jogador.revives += self.valor

class VidaMaxima(Efeito): #atualmente não funciona muito bem porque o sprite não mostra nada acima de 100 de HP
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.hpMax += self.valor

class DecaimentoVida(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.base_rate = jogador.base_rate*self.valor


class Item:
    def __init__(self, nome: str, descricao: str, efeitos: list, sprite, raridade: str, id: int):
        self.nome = nome
        self.descricao = descricao
        self.efeitos = efeitos
        self.sprite = sprite
        self.raridade = raridade
        self.id = id

    def aplicar_em(self, jogador):
        for efeito in self.efeitos:
            efeito.aplicar(jogador)


class ItemAtivo:
    def __init__(self, nome: str, descricao: str, usos: int, efeitos: list, afetaIni: bool, sprite, raridade: str, id: int, listaInimigos=None, player=None):
        self.nome = nome
        self.descricao = descricao
        self.efeitos = efeitos
        self.usos = usos
        self.listaInimigos = listaInimigos
        self.player = player
        self.afetaIni = afetaIni
        self.sprite = sprite
        self.raridade = raridade
        self.id = id
        self.efeitos_ativos = []  # Para rastrear quais efeitos foram aplicados

    def aplicar_em(self):
        if self.afetaIni:
            for efeito in self.efeitos:
                for inimigo in self.listaInimigos:
                    efeito.aplicar(inimigo)
                    self.efeitos_ativos.append(efeito)
        else:
            for efeito in self.efeitos:
                efeito.aplicar(self.player)
                self.efeitos_ativos.append(efeito)

    def remover_efeitos(self, player=None):
        if not self.afetaIni and player:
            for efeito in self.efeitos_ativos:
                if hasattr(efeito, 'remover'):
                    efeito.remover(player)
            self.efeitos_ativos = []