from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from random import randint, choice
from abc import ABC, abstractmethod
from som import GerenciadorDeSom
from som import som
from dificuldade import dificuldade_global

# raridade
RARIDADES = {
    "comum": 1,
    "incomum": 2,
    "rara": 3,
    "lendária": 4
}


# classe modificador
class Modificador(ABC):
    @abstractmethod
    def aplicarMod(self, arma):
        pass


# classe arma
class Arma(ABC):
    @abstractmethod
    def aplicaModificador(self):
        pass

    def ataquePrincipal(self, inimigo):
        pass

    def ataqueSecundario(self, inimigo):
        pass

    def get_save_data(self):
        return {
            'tipo': self.__class__.__name__,
            'raridade': self.raridadeStr,
            'dano': self.dano,
            'velocidade': self.velocidade,
            'lifeSteal': self.lifeSteal,
            'chanceCritico': self.chanceCritico,
            'danoCriticoMod': self.danoCriticoMod,
            'modificador': self.modificador.nome if hasattr(self, 'modificador') else None,
            'modificador_detalhes': {
                'nome': self.modificador.nome,
                'valor': self.modificador.valor
            } if hasattr(self, 'modificador') else None
        }

    def load_save_data(self, data, lista_mods=None):
        self.dano = data['dano']
        self.velocidade = data['velocidade']
        self.lifeSteal = data['lifeSteal']
        self.chanceCritico = data['chanceCritico']
        self.danoCriticoMod = data['danoCriticoMod']

        if data['modificador'] and lista_mods:
            mod_class = getattr(sys.modules[__name__], data['modificador'])
            self.modificador = mod_class(self)
            if data.get('modificador_detalhes'):
                self.modificador.valor = data['modificador_detalhes']['valor']

        self.aplicaModificador()


# MODIFICADORES:
class Amaldicoado(Modificador):
    def __init__(self, arma):
        self.nome = "Amaldicoado"
        self.atributos = ["dano", "velocidade", "lifeSteal", "chanceCritico", "danoCriticoMod"]

        self.atributo_bom = choice(self.atributos)
        self.atributo_ruim = choice([a for a in self.atributos if a != self.atributo_bom])

        self.valor = {
            "bom": round(randint(100, 200) / 10, 1),   # de +10.0 até +20.0
            "ruim": round(randint(50, 150) / 10, 1)   # de -10.0 até -20.0
        }

    def aplicarMod(self, arma):
        valor_bom = self.valor["bom"]
        setattr(arma, self.atributo_bom, getattr(arma, self.atributo_bom) + valor_bom)
        valor_ruim = self.valor["ruim"]
        setattr(arma, self.atributo_ruim, max(0, getattr(arma, self.atributo_ruim) - valor_ruim))

class Rapida(Modificador):
    def __init__(self, arma):
        self.valor = randint(15 + arma.raridade, 30 + arma.raridade) / 10
        self.nome = "Rapida"

    def aplicarMod(self, arma):
        arma.velocidade = self.valor
        arma.dano -= self.valor


class Afiada(Modificador):
    def __init__(self, arma):
        self.valor = arma.dano * 0.5 + arma.raridade * 5
        self.nome = "Afiada"

    def aplicarMod(self, arma):
        arma.dano += self.valor


class Precisa(Modificador):
    def __init__(self, arma):
        self.valor = 5 * arma.raridade
        self.nome = "Precisa"

    def aplicarMod(self, arma):
        arma.chanceCritico += self.valor


class Impactante(Modificador):
    def __init__(self, arma):
        self.valor = arma.raridade
        self.nome = "Impactante"

    def aplicarMod(self, arma):
        arma.danoCriticoMod += self.valor


class Sangrenta(Modificador):
    def __init__(self, arma):
        self.valor = arma.lifeSteal / 2
        self.nome = "Sangrenta"

    def aplicarMod(self, arma):
        arma.lifeSteal += self.valor


class Pesada(Modificador):
    def __init__(self, arma):
        self.valor = arma.dano
        self.nome = "Pesada"

    def aplicarMod(self, arma):
        arma.dano += self.valor
        arma.velocidade *= 0.8


class Sortuda(Modificador):
    def __init__(self, arma):
        self.valor = arma.chanceCritico * 4
        self.nome = "Sortuda"

    def aplicarMod(self, arma):
        arma.chanceCritico += self.valor
        arma.danoCriticoMod *= 0.8


class Potente(Modificador):
    def __init__(self, arma):
        self.valor = 2 * arma.raridade
        self.nome = "Potente"

    def aplicarMod(self, arma):
        arma.danoCriticoMod += self.valor
        arma.chanceCritico *= 0.5


class ListaMods:
    def __init__(self):
        self.modificadores = [
            Rapida, Afiada, Precisa,
            Impactante, Sangrenta, Pesada,
            Sortuda, Potente, Amaldicoado
        ]

        self.modificadores_por_nome = {
            cls.__name__: cls for cls in self.modificadores
        }

    def get_mod_by_name(self, nome):
        """Obtém uma classe de modificador pelo nome"""
        return self.modificadores_por_nome.get(nome)

    def getMod(self, raridade_str):
        """Retorna um modificador aleatório, sem restrição por raridade"""
        return choice(self.modificadores)


#ARMAS:
class LaminaDaNoite(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Lamina da Noite"
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
        self.carta = 'assets/Itens/Carta_espada_lunar.png'
        self.size = (20 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final * self.comboMult
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final * self.comboMult

    def ataqueSecundario(self,inimigo,player):
        current_time = time.get_ticks()
        custo = 50  * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            inimigo.congelado = True
            player.mp -= custo
            player.last_dash_time = current_time

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
        self.carta = 'assets/Itens/Carta_espada_sangue.png'
        self.size = (20 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

        self.valorSangramento = 2.2*self.raridade

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final

    def ataqueSecundario(self,inimigo,player):
        current_time = time.get_ticks()
        custo = 40 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            player.mp -= custo
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
        self.lifeSteal = self.dano/2
        self.chanceCritico = 5
        self.danoCriticoMod = 2
        self.comboMult = 1
        self.clock = time.Clock()

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/Karambit.png"
        self.sprite = 'assets/player/Karambit.png'
        self.carta = 'assets/Itens/Carta_Adaga.png'
        self.size = (32*2,32*2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"


    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final

    def ataqueSecundario(self,inimigo,player):
        current_time = time.get_ticks()
        custo = 40 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            player.mp -= custo
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
        self.carta = 'assets/Itens/Carta_titã.png'
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
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final
        self.chanceCritico = self.criticoOg
        self.danoCriticoMod = self.danoCritOg


    def ataqueSecundario(self,player):
        current_time = time.get_ticks()
        custo = 50 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if self.chanceCritico > 100 or player.mp <= 0:
            return
        else:
            som.tocar('carrega_critico')
            self.chanceCritico *= 2
            self.danoCriticoMod *= 1.5
            player.mp -= custo


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

        self.secEhAtaque = True
        self.ehRanged = False
        self.ehAOE = False

        self.spriteIcon = "assets/UI/machadodoinverno.png"
        self.sprite = 'assets/player/machadodoinverno.png'
        self.carta = 'assets/Itens/Carta_machado_gelo.png'
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
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if inimigo.congelado: #da crit se o inimigo estiver congelado
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
            inimigo.congelado = False
            inimigo.velocidade /= 0.25
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final
        self.chanceCritico = self.criticoOg
        self.danoCriticoMod = self.danoCritOg

    def ataqueSecundario(self, inimigo,player):
        current_time = time.get_ticks()
        custo = 35 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            inimigo.velocidade *= 0.25
            inimigo.congelado = True
            player.mp -= custo
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
        self.carta = 'assets/Itens/Carta_espada_laser.png'
        self.size = (23 * 2, 54 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,inimigo):
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final


    def ataqueSecundario(self,player,mouse_pos):
        current_time = time.get_ticks()
        custo = 20 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            player.criar_projetil(mouse_pos,(self.dano/2.5),cor=(24,212,59))
            player.mp -= custo
            player.last_dash_time = current_time


class MarteloSolar(Arma):
    def __init__(self,raridadeStr : str,listaMods : ListaMods):
        self.tipoDeArma = "Martelo Solar"
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
        self.carta = 'assets/Itens/Carta_Sol.png'
        self.size = (27 * 2, 51 * 2)
        self.pivot = (self.size[0] / 2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)

    def ataquePrincipal(self,inimigo):
        dano_final = self.dano * inimigo.modificadorDanoRecebido * dificuldade_global.mult_dano_inimigo * self.comboMult
        if randint(1, 100) <= self.chanceCritico:
            inimigo.hp -= dano_final * self.danoCriticoMod
            inimigo.ultimo_dano_critico = True
            inimigo.ultimo_dano = dano_final * self.danoCriticoMod
        else:
            inimigo.hp -= dano_final
            inimigo.ultimo_dano_critico = False
            inimigo.ultimo_dano = dano_final

    def ataqueSecundario(self,player,mouse_pos):
        current_time = time.get_ticks()
        custo = 30 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp-(30* player.mpModificador) < 0:
            return #revisar isso
        else:
            som.tocar('martelo2')
            aoeMartelo = player.criarAOE(mouse_pos, 300)
            if aoeMartelo is None:
                return
            player.mp -= custo
            player.last_dash_time = current_time
            return aoeMartelo


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
        self.carta = 'assets/Itens/Carta_Arco.png'
        self.size = (51 * 2, 27 * 2)
        self.pivot = (self.size[0]/2, 0)

        mod_classe = listaMods.getMod(self.raridadeStr)  # Retorna a classe do modificador
        self.modificador = mod_classe(self)  # Instancia com self (a arma)
        self.nome = f"{self.tipoDeArma} {self.modificador.nome} {self.raridadeStr}"

    def aplicaModificador(self):
        self.modificador.aplicarMod(self)
    def ataquePrincipal(self,player,mouse_pos):
        dano_final = self.dano * dificuldade_global.mult_dano_inimigo * self.comboMult
        som.tocar('arco_acerto')
        sprite_projetil = image.load("assets/player/flecha.png").convert_alpha()
        player.criar_projetil(mouse_pos, dano=dano_final, cor=None, sprite=sprite_projetil)


    def ataqueSecundario(self,player,mouse_pos):
        dano_final = self.dano * dificuldade_global.mult_dano_inimigo * self.comboMult
        sprite_projetil = image.load("assets/player/flecha.png").convert_alpha()
        angulo_central = player.calcular_angulo(mouse_pos)
        angulo_abertura = math.radians(5)  # 15 graus em radianos
        current_time = time.get_ticks()
        custo = 20 * player.mpModificador
        if player.mp < custo:
            # Ativa mensagem de sem mana no HUD
            player.hud.mensagem_sem_mana = True
            player.hud.tempo_mensagem_mana = current_time
            return
        if player.mp <= 0:
            return
        else:
            som.tocar('tripleshota')
            player.mp -= custo
            player.last_dash_time = current_time
            player.criar_projetil(mouse_pos, dano=dano_final, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central)
            player.criar_projetil(mouse_pos, dano=dano_final, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central - angulo_abertura)
            player.criar_projetil(mouse_pos, dano=dano_final, cor=None, sprite=sprite_projetil, angulo_personalizado=angulo_central + angulo_abertura)




