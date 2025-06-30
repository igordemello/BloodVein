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
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 10+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 1 #analisar esses valores depois
        self.cooldown = 400
        self.range = (40, 90) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 8
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/LaminaDaNoite.png"
        self.sprite = 'espada.png'
        self.size = (20 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,inimigo,player):
        return False

#falta sprite e animação de ataque
class Chigatana(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Chigatana"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 10+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 2 #analisar esses valores depois
        self.cooldown = 400
        self.range = (35, 90) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/4
        self.chanceCritico = 5
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/chigatana.png"
        self.sprite = 'assets/player/chigatana.png'
        self.size = (20 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

        self.valorSangramento = 2.2*self.raridade

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,inimigo,player):
        inimigo.modificadorDanoRecebido = self.valorSangramento


class Karambit(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Adaga"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 5+randint(5*self.raridade,10*self.raridade)
        self.velocidade = 2 #analisar esses valores depois
        self.cooldown = 300
        self.range = (50, 50) #hitbox arma
        self.radius = 80
        self.efeitos = None
        self.lifeSteal = self.dano/4
        self.chanceCritico = 5
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/Karambit.png"
        self.sprite = 'assets/player/Karambit.png'
        self.size = (32*2,32*2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

        self.valorSangramento = 2.2*self.raridade

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,inimigo,player):
        inimigo.envenenar(5, self.dano+10)


class EspadaDoTita(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Espada do Tita"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 25+randint(15*self.raridade,25*self.raridade)
        self.velocidade = 0.5 #analisar esses valores depois
        self.cooldown = 400
        self.range = (40, 115) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 12
        self.danoCriticoMod = 3
        self.comboMult = 1
        self.clock = time.Clock()
        self.criticoOg = self.chanceCritico
        self.danoCritOg = self.danoCriticoMod

        self.secEhAtaque = False
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/espadadotita.png"
        self.sprite = 'assets/player/espadadotita.png'
        self.size = (25 * 2, 70 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
        self.criticoOg = self.chanceCritico
        self.danoCritOg = self.danoCriticoMod
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult
        self.chanceCritico = self.criticoOg
        self.danoCriticoMod = self.danoCritOg


    def ataqueSecundario(self,player):
        if self.chanceCritico > 100 or player.st <= 0:
            return
        else:
            self.chanceCritico *= 2
            self.danoCriticoMod *= 1.5
            player.st -= 50


class MachadoDoInverno(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Machado Do Inverno"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 15+randint(15*self.raridade,25*self.raridade)
        self.velocidade = 0.7 #analisar esses valores depois
        self.cooldown = 400
        self.range = (40, 80) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 15
        self.danoCriticoMod = 1.5
        self.comboMult = 1
        self.clock = time.Clock()
        self.criticoOg = self.chanceCritico
        self.danoCritOg = self.danoCriticoMod

        self.congelou = False

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/machadodoinverno.png"
        self.sprite = 'assets/player/machadodoinverno.png'
        self.size = (23 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
        self.criticoOg = self.chanceCritico
        self.danoCritOg = self.danoCriticoMod
    def ataquePrincipal(self,inimigo):
        if inimigo.congelado: #da crit se o inimigo estiver congelado
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.congelado = False
            inimigo.velocidade /= 0.25
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult
        self.chanceCritico = self.criticoOg
        self.danoCriticoMod = self.danoCritOg

    def ataqueSecundario(self, inimigo,player):
        current_time = time.get_ticks()
        if player.st <= 0:
            return
        else:
            inimigo.velocidade *= 0.25
            inimigo.congelado = True
            player.st -= 50
            player.last_dash_time = current_time

class EspadaEstelar(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Espada Estelar"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 20+randint(10*self.raridade,20*self.raridade)
        self.velocidade = 0.8 #analisar esses valores depois
        self.cooldown = 400
        self.range = (40, 90) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 10
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = True
        self.ehAOE = False

        self.spriteIcon = "assets/UI/espadaestelar.png"
        self.sprite = 'assets/player/espadaestelar.png'
        self.size = (23 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult


    def ataqueSecundario(self,player,mouse_pos):
        current_time = time.get_ticks()
        if player.st <= 0:
            return
        else:
            player.criar_projetil(mouse_pos,(self.dano/2.5),cor=(24,212,59))
            player.st -= 20
            player.last_dash_time = current_time


class MarteloSolar(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Machado Do Inverno"
        self.ataqueTipo = "melee"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 15+randint(15*self.raridade,25*self.raridade)
        self.velocidade = 0.5 #analisar esses valores depois
        self.cooldown = 400
        self.range = (52, 80) #hitbox arma
        self.radius = 100
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 13
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = True
        self.ehAOE = True
        self.danoAOE = self.dano*0.8


        self.spriteIcon = "assets/UI/martelo_icone.png"
        self.sprite = 'assets/player/martelo_solar.png'
        self.size = (27 * 2, 51 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)

    def ataquePrincipal(self,inimigo):
        if randint(1, 100) <= self.chanceCritico:
            original_speed = self.clock.get_fps()
            self.clock.tick(original_speed)
            inimigo.hp -= self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = self.dano * self.danoCriticoMod * inimigo.modificadorDanoRecebido * self.comboMult
        else:
            inimigo.hp -= self.dano * inimigo.modificadorDanoRecebido * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = self.dano * self.comboMult

    def ataqueSecundario(self,player,mouse_pos):
        current_time = time.get_ticks()
        if player.st-50 <= 0:
            return #revisar isso
        else:
            player.st -= 50
            player.last_dash_time = current_time
            return player.criarAOE(mouse_pos, 300)


class Arco(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Arco"
        self.ataqueTipo = "ranged"
        self.raridadeStr = raridadeStr
        self.raridade = RARIDADES.get(self.raridadeStr, 1)
        self.dano = 20+randint(10*self.raridade,20*self.raridade)
        self.velocidade = 1 #analisar esses valores depois
        self.cooldown = 400
        self.range = (40, 90) #hitbox arma
        self.radius = 90
        self.efeitos = None
        self.lifeSteal = self.dano/2
        self.chanceCritico = 10
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = True
        self.ehAOE = False

        self.spriteIcon = "assets/UI/arco.png"
        self.sprite = 'assets/player/arco.png'
        self.size = (51 * 2, 27 * 2)
        self.pivot = (self.size[0]/2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,player,mouse_pos):
        sprite_projetil = image.load("assets/player/flecha.png").convert_alpha()
        player.criar_projetil(mouse_pos, dano=self.dano, cor=None, sprite=sprite_projetil)


    def ataqueSecundario(self,player,mouse_pos):
        sprite_projetil = image.load("assets/player/flecha.png").convert_alpha()

        angulo_central = player.calcular_angulo(mouse_pos)
        angulo_abertura = math.radians(5)  # 15 graus em radianos
        current_time = time.get_ticks()
        if player.st <= 0:
            return
        else:
            player.st -= 20
            player.last_dash_time = current_time
            player.criar_projetil(mouse_pos, dano=self.dano, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central)
            player.criar_projetil(mouse_pos, dano=self.dano, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central - angulo_abertura)
            player.criar_projetil(mouse_pos, dano=self.dano, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central + angulo_abertura)




