from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *

class ConjuntoItens :
   def __init__(self):
      self.itens = {
        "Chapéu de bruxa" : Item(
            nome="Chapéu de bruxa",
            descricao="Aumenta seu dano",
            efeitos=[
            DanoUsuario(20,"+"),
            ],
            id=1,
        ),
        "Sapato de Sangue" : Item(
           nome="Sapato de Sangue",
           descricao="Aumenta sua velocidade",
           efeitos=[
              VelocidadeMovimento(0.5)
           ],
            id=2,
        ),
        "Luva de Titã" : Item(
           nome="Luva de Titã",
           descricao="Diminui a duração do ataque",
           efeitos=[
              VelocidadeAtaque(1) #temporário, nada disso funciona
           ],
            id=3,
        ),
        "Seringa de Sangue" : Item(
           nome="Seringa de Sangue",
           descricao="Diminui o decaimento de vida",
           efeitos=[
              DecaimentoVida(0.75) #transforma em 75%
           ],
            id=4,
        ),
        "Varinha mágica" : Item(
           nome="Varinha Mágica",
           descricao="Aumenta o dano",
           efeitos=[
              DanoUsuario(1.5,"*")
           ],
            id=5,
        ),
        "Água Benta" : Item(
           nome="Água Benta",
           descricao="Duplica a velocidade do decaimento e duplica o seu dano",
           efeitos=[
              DanoUsuario(2,"*")
           ],
            id=6,
        ),
        "Coração Humano" : Item(
           nome="Coração Humano",
           descricao="Sua vida não decaí mais, mas ela é reduzida pela metade",
           efeitos=[
              VidaMaxima(-50),
              DecaimentoVida(0.75)
           ],
            id=7
        ),
        "Caixão do Papa Vamp" : Item(
           nome="Caixão do Papa Vamp",
           descricao="Ao morrer, você revive uma vez",
           efeitos=[
              Revives(1)
           ],
            id=8,
        ),
        #Itens Ativos:
        "Crucifixo Invertido" : ItemAtivo(
            nome="Crucifixo Invertido",
            descricao="Aumenta seu dano temporariamente na sala atual",
            usos = 2,
            efeitos=[
                DanoUsuario(20)
            ],
            afetaIni=False,
            id=9,
        ),
        "Aranha de brinquedo" : ItemAtivo(
            nome="Aranha de brinquedo",
            descricao="Aumenta sua velocidade nesta sala",
            usos=3,
            efeitos=[
                VelocidadeMovimento(1)
            ],
            afetaIni=False,
            id=10,
        ),
        "Dentadura" : ItemAtivo(
            nome="Dentadura",
            descricao="Dá dano em todos os inimigos nesta sala",
            usos=2,
            efeitos=[
                DarDano(20)
            ],
            afetaIni=True,
            id=11,
        )




        
        }
