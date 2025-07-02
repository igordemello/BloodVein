from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from abc import ABC, abstractmethod
from typing import Optional
from random import choice

'''
Comum:
Forte - Mais dano
Resistente - Mais vida
Ligeiro - Mais veloz
Dobro - Ataca em dobro

Canhão de Vidro - Dobro de dano, metade da vida base
Parrudo - Dobro de vida, metade do dano
Resistente - Recebe apenas metade do dano
'''
class ModificadorInimigo(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def nome(self) -> str:
        pass

    @abstractmethod
    def aplicar(self, inimigo) -> None:
        pass


# Modificadores Comuns (sufixos)
class Resistente(ModificadorInimigo):
    @property
    def nome(self):
        return "Resistente"

    def aplicar(self, inimigo):
        inimigo.hp_max *= 1.2
        inimigo.hp = inimigo.hp_max


class Forte(ModificadorInimigo):
    @property
    def nome(self):
        return "Forte"

    def aplicar(self, inimigo):
        inimigo.dano *= 1.5


class Ligeiro(ModificadorInimigo):
    @property
    def nome(self):
        return "Ligeiro"

    def aplicar(self, inimigo):
        inimigo.velocidade *= 1.5
        inimigo.dano *= 0.9


# Modificadores Especiais
class CanhaoDeVidro(ModificadorInimigo):
    @property
    def nome(self):
        return "Canhão de Vidro"

    def aplicar(self, inimigo):
        inimigo.dano *= 2.0
        inimigo.hp_max *= 0.5
        inimigo.hp = min(inimigo.hp, inimigo.hp_max)


class Parrudo(ModificadorInimigo):
    @property
    def nome(self):
        return "Parrudo"

    def aplicar(self, inimigo):
        inimigo.hp_max *= 2.0
        inimigo.dano *= 0.7
        inimigo.hp = inimigo.hp_max


# Modificador Elite
class Congelante(ModificadorInimigo):
    @property
    def nome(self):
        return "Congelante"

    def aplicar(self, inimigo):
        inimigo.pode_congelar = True

class Amaldicoado(ModificadorInimigo):
    @property
    def nome(self):
        return "Amaldiçoado"
    def aplicar(self, inimigo):
        inimigo.pode_sangramento = True

class Nojento(ModificadorInimigo):
    @property
    def nome(self):
        return "Nojento"
    def aplicar(self, inimigo):
        inimigo.pode_envenenar = True

class Sortudo(ModificadorInimigo):
    @property
    def nome(self):
        return "Sortudo"
    def aplicar(self, inimigo):
        inimigo.pode_critar = True

class Amedrontador(ModificadorInimigo):
    @property
    def nome(self):
        return "Amedrontador"
    def aplicar(self, inimigo):
        inimigo.pode_enfraquecer = True


class GerenciadorModificadores:
    def __init__(self):
        self.modificadores_comuns = [Resistente,Forte,Ligeiro,CanhaoDeVidro,Parrudo]
        self.modificadores_elite = [Congelante,Amaldicoado,Nojento,Sortudo,Amedrontador]

    def get_modificador_comum(self):
        return choice(self.modificadores_comuns)()

    def get_modificador_elite(self):
        return choice(self.modificadores_elite)()

    def aplicar_modificadores(self, inimigo, elite=False):
        if not elite:
            modificador = self.get_modificador_comum()
            modificador.aplicar(inimigo)
            inimigo.nome = f"{inimigo.nome_base} {modificador.nome}"
        else:
            prefixo = self.get_modificador_elite()
            sufixo = self.get_modificador_comum()

            prefixo.aplicar(inimigo)
            sufixo.aplicar(inimigo)
            inimigo.nome = f"{prefixo.nome} {inimigo.nome_base} {sufixo.nome}"