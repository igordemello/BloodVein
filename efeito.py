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
stamina
debuffVeneno
tempo de invencibilidade (A)
velocidade de movimento DOS INIMIGOS (A)
'''

#todos os efeitos são incrementais "+=". em casos de item que os afetam negativamente (exemplo: aumenta a velocidade de decaimento, nesse caso o valor seria só X mesmo, mas no caso de dimuinuir a velocidade de decaimento, se usaria X negativo)
class Efeito(ABC):
    @abstractmethod
    def aplicar(self,jogador):
        pass
    def remover(self,jogador): 
        pass

class DanoUsuario(Efeito):
    def __init__(self, valor,tipoInc=str):
        self.valor = valor
        self.tipoInc = tipoInc
        self.valorOriginal = None
        self.ativo = False
    def aplicar(self, jogador):
        if not self.ativo:
            if self.tipoInc == "+":
                self.valorOriginal = jogador.arma.dano
                jogador.arma.dano += self.valor
            else:
                self.valorOriginal = jogador.arma.dano
                jogador.arma.dano = jogador.arma.dano*self.valor
                self.ativo = True
    def remover(self,jogador):
        if self.ativo and self.valorOriginal is not None:
            if self.tipoInc == "+":
                jogador.arma.dano = self.valorOriginal
                self.ativo = False
            else:
                jogador.arma.dano = self.valorOriginal
                self.ativo = False

class ModificadorDanoRecebido(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self,jogador):
        jogador.modificadorDanoRecebido *= self.valor

class CooldownStamina(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self,jogador):
        jogador.cooldown_st -= self.valor

class CooldownDash(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self,jogador):
        jogador.dash_cooldown_max -= self.valor

class DuraçãoDash(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self,jogador):
        jogador.dash_duration_max += self.valor

class CustoDash(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self,jogador):
        jogador.custoDash -= self.valor

class DarDano(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.hp -= self.valor

class VidaMaxima(Efeito): #atualmente não funciona muito bem porque o sprite não mostra nada acima de 100 de HP
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.hpMax += self.valor 

class VelocidadeAtaque(Efeito):
    def __init__(self, valor):
        self.valor = valor
    def aplicar(self, jogador):
        jogador.arma.velocidade += self.valor #deixa o ataque mais rapido (a animação  também)

class VelocidadeMovimento(Efeito):
    def __init__(self, valor):
        self.valor = valor
        self.valor_original = None
        self.ativo = False
    
    def aplicar(self, jogador):
        if not self.ativo:
            self.valor_original = jogador.velocidadeMov
            jogador.velocidadeMov += self.valor
            self.ativo = True
    
    def remover(self, jogador):
        if self.ativo and self.valor_original is not None:
            # Aplica um fade out suave da velocidade
            jogador.velocidadeMov = self.valor_original
            jogador.vx *= 0.5  # Reduz gradualmente
            jogador.vy *= 0.5
            self.ativo = False
            
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

    
class Item: #mudar o nome depois pra ItemPassivo
    def __init__(self, nome: str, descricao: str, efeitos: list,sprite,raridade : str,id : int):
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
    def __init__(self, nome: str, descricao: str, usos: int, efeitos: list, afetaIni : bool, sprite,raridade : str,id: int,listaInimigos = None, player = None):
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

    def aplicar_em(self):
        if self.afetaIni:
            for efeito in self.efeitos:
                for inimigo in self.listaInimigos:
                    efeito.aplicar(inimigo)
        else:
            for efeito in self.efeitos:
                efeito.aplicar(self.player)

    def remover_efeitos(self,player):
        if not self.afetaIni:
            for efeito in self.efeitos:
                efeito.remover(player)




'''    
exemplo de um item ativo que afeta inimigos
ItemAtivo(
            nome="Cu",
            descricao="Cu",
            usos=2,
            efeitos=[
                DarDano(100)
            ],
            afetaIni=True,
        )
'''