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
            usos = 0,
            efeitos=[
            DanoUsuario(20,"+"),
            ] 
        ),
        "Sapato de Sangue" : Item(
           nome="Sapato de Sangue",
           descricao="Aumenta sua velocidade",
           usos = 0,
           efeitos=[
              VelocidadeMovimento(0.5)
           ]
        ),
        "Luva de Titã" : Item(
           nome="Luva de Titã",
           descricao="Diminui a duração do ataque",
           usos = 0,
           efeitos=[
              VelocidadeAtaque(1) #temporário, nada disso funciona
           ]
        ),
        "Seringa de Sangue" : Item(
           nome="Seringa de Sangue",
           descricao="Diminui o decaimento de vida",
           usos = 0,
           efeitos=[
              DecaimentoVida(0.75) #transforma em 75%
           ]
        ),
        "Varinha mágica" : Item(
           nome="Varinha Mágica",
           descricao="Aumenta o dano",
           usos = 0,
           efeitos=[
              DanoUsuario(1.5,"*")
           ]
        ),
        "Água Benta" : Item(
           nome="Água Benta",
           descricao="Duplica a velocidade do decaimento e duplica o seu dano",
           usos = 0,
           efeitos=[
              DanoUsuario(2,"*")
           ]
        ),
        "Coração Humano" : Item(
           nome="Coração Humano",
           descricao="Sua vida não decaí mais, mas ela é reduzida pela metade",
           usos = 0,
           efeitos=[
              VidaMaxima(-50),
              DecaimentoVida(0.75)
           ]
        ),
        "Caixão do Papa Vamp" : Item(
           nome="Caixão do Papa Vamp",
           descricao="Ao morrer, você revive uma vez",
           usos = 0,
           efeitos=[
              Revives(1)
           ]
        ),

        
        }
