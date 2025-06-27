from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import randint,choice
from abc import ABC, abstractmethod
#raridade
RARIDADES = {
    "comum": 1,
    "rara": 2,
    "lendária": 3
}


#classe modificador
class Modificador(ABC):
    @abstractmethod

    def aplicarMod(self, arma):
        pass

#classe arma
class Arma(ABC):
    @abstractmethod

    def aplicaModificador(self):
        pass
    def ataquePrincipal(self,inimigo):
        pass
    def ataqueSecundario(self,inimigo):
        pass


#MODIFICADORES:
class BainhaRapida(Modificador):
    def __init__(self,arma):
        self.valor = randint(15+arma.raridade,30+arma.raridade)/10
        self.nome = "Rapida"

    def aplicarMod(self, arma):
        arma.velocidade = self.valor
        arma.dano -= self.valor

class Afiada(Modificador):
    def __init__(self,arma):
        self.valor = arma.dano*0.5+arma.raridade*5
        self.nome = "Afiada"
    def aplicarMod(self, arma):
        arma.dano += self.valor

class Precisa(Modificador):
    def __init__(self,arma):
        self.valor = 5*arma.raridade
        self.nome = "Precisa"
    def aplicarMod(self, arma):
        arma.chanceCritico += self.valor

class Impactante(Modificador):
    def __init__(self,arma):
        self.valor = arma.raridade
        self.nome = "Impactante"
    def aplicarMod(self, arma):
        arma.danoCriticoMod += self.valor

class Sangrenta(Modificador):
    def __init__(self,arma):
        self.valor = arma.lifeSteal/2
        self.nome = "Sangrenta"
    def aplicarMod(self, arma):
        arma.lifeSteal += self.valor

class Pesada(Modificador):
    def __init__(self,arma):
        self.valor = arma.dano
        self.nome = "Pesada"
    def aplicarMod(self, arma):
        arma.dano += self.valor
        arma.velocidade *= 0.5

class Sortuda(Modificador):
    def __init__(self,arma):
        self.valor = arma.chanceCritico * 10
        self.nome = "Sortuda"
    def aplicarMod(self, arma):
        arma.chanceCritico += self.valor
        arma.danoCriticoMod *= 0.8

class Potente(Modificador):
    def __init__(self,arma):
        self.valor = 2*arma.raridade
        self.nome = "Potente"
    def aplicarMod(self, arma):
        arma.danoCriticoMod += self.valor
        arma.chanceCritico *= 0.5


class ListaMods:
    def __init__(self):
        self.modificadores_por_raridade = {
            "comum": [BainhaRapida, Afiada, Precisa],
            "rara": [Impactante, Sangrenta, Pesada],
            "lendária": [Sortuda, Potente],
        }

    def getMod(self, raridade_str):
        mods = self.modificadores_por_raridade.get(raridade_str.lower(), [])
        if mods:
            return choice(mods)




#ARMAS:
class LaminaDaNoite(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Lámina da Noite"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 10+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 1 #analisar esses valores depois
        self.cooldown = 400
        self.range = (70, 100) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 8
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            time.delay(100)
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self):
        return False

#falta sprite e animação de ataque
class Chigatana(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Chigatana"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 10+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 2 #analisar esses valores depois
        self.cooldown = 400
        self.range = (70, 100) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/4
        self.chanceCritico = 5
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

        self.valorSangramento = 2.2*self.raridade

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            time.delay(100)
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,inimigo):
        inimigo.modificadorDanoRecebido = self.valorSangramento


class Karambit(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Adaga"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 10+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 2 #analisar esses valores depois
        self.cooldown = 300
        self.range = (45, 90) #hitbox arma
        self.radius = 50
        self.efeitos = None
        self.lifeSteal = self.dano/4
        self.chanceCritico = 5
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

        self.valorSangramento = 2.2*self.raridade

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            time.delay(100)
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,inimigo):
        inimigo.envenenar(5, self.dano)


