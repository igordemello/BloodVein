from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from abc import ABC, abstractmethod
'''
dano do usuario ✓
vida maxima ✓
velocidade de ataque ✓
velocidade de movimento ✓
decaimento de vida ✓
revives ✓
debuffVeneno
tempo de invencibilidade (A)
velocidade de movimento DOS INIMIGOS (A)
'''

#todos os efeitos são incrementais "+=". em casos de item que os afetam negativamente (exemplo: aumenta a velocidade de decaimento, nesse caso o valor seria só X mesmo, mas no caso de dimuinuir a velocidade de decaimento, se usaria X negativo)
class Efeito(ABC):
    @abstractmethod
    def aplicar(self,jogador):
        pass

class DanoUsuario(Efeito):
    def __init__(self, valor,tipoInc=str):
        self.valor = valor
        self.tipoInc = tipoInc
    def aplicar(self, jogador):
        if self.tipoInc == "+":
            jogador.dano += self.valor
        else:
            jogador.dano = jogador.dano*self.valor

class VidaMaxima(Efeito): #atualmente não funciona muito bem porque o sprite não mostra nada acima de 100 de HP
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.hpMax += self.valor 

class VelocidadeAtaque(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.velocidadeAtk += self.valor #deixa o ataque mais rapido (a animação  também)

class VelocidadeMovimento(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.velocidadeMov += self.valor

class DecaimentoVida(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.rate = jogador.rate*self.valor

class Revives(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.revives += self.valor

    
class Item:
    def __init__(self, nome: str, descricao: str, usos: int, efeitos: list):
        self.nome = nome
        self.descricao = descricao
        self.efeitos = efeitos  
        self.usos = usos

    def aplicar_em(self, jogador):
        for efeito in self.efeitos:
            efeito.aplicar(jogador)


    

