from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *


class ConjuntoItens:
    def __init__(self):
        self.itens = {
            "Chapéu de bruxa": Item(
                nome="Chapéu de bruxa",
                descricao="Aumenta seu dano",
                efeitos=[
                    DanoUsuario(20, "+"),
                ],
                sprite=image.load("assets\itens\ChapeuDeBruxa.png").convert_alpha(),
                raridade = "comum",
                id=1,
            ),
            "Sapato de Sangue": Item(
                nome="Sapato de Sangue",
                descricao="Aumenta sua velocidade",
                efeitos=[
                    VelocidadeMovimento(0.5)
                ],
                sprite=image.load("assets\itens\Botasdesangue.png").convert_alpha(),
                raridade="comum",
                id=2,
            ),
            "Luva de Titã": Item(
                nome="Luva de Titã",
                descricao="Diminui a duração do ataque",
                efeitos=[
                    VelocidadeAtaque(1)  #temporário, nada disso funciona
                ],
                sprite=image.load("assets\itens\LuvaDeTita.png").convert_alpha(),
                raridade="comum",
                id=3,
            ),
            "Seringa de Sangue": Item(
                nome="Seringa de Sangue",
                descricao="Diminui o decaimento de vida",
                efeitos=[
                    DecaimentoVida(0.75)  #transforma em 75%
                ],
                sprite=image.load("assets\itens\SeringaDeSangue.png").convert_alpha(),
                raridade="rara",
                id=4,
            ),
            "Varinha mágica": Item(
                nome="Varinha Mágica",
                descricao="Aumenta o dano",
                efeitos=[
                    DanoUsuario(1.5, "*")
                ],
                sprite=image.load("assets\itens\ChapeuDeBruxa.png").convert_alpha(),
                raridade="rara",
                id=5,
            ),
            "Água Benta": Item(
                nome="Água Benta",
                descricao="Duplica a velocidade do decaimento e duplica o seu dano",
                efeitos=[
                    DanoUsuario(2, "*"),
                    DecaimentoVida(2)
                ],
                sprite=image.load("assets\itens\AguaBenta.png").convert_alpha(),
                raridade="rara",
                id=6,
            ),
            "Coração Humano": Item(
                nome="Coração Humano",
                descricao="Sua vida não decaí mais, mas ela é reduzida pela metade",
                efeitos=[
                    VidaMaxima(-50),
                    DecaimentoVida(0)
                ],
                sprite=image.load("assets\itens\ChapeuDeBruxa.png").convert_alpha(),
                raridade="lendaria",
                id=7
            ),
            "Caixão do Papa Vamp": Item(
                nome="Caixão do Papa Vamp",
                descricao="Ao morrer, você revive uma vez",
                efeitos=[
                    Revives(1)
                ],
                sprite=image.load("assets\itens\ChapeuDeBruxa.png").convert_alpha(),
                raridade="lendaria",
                id=8,
            ),
            #Itens Ativos:
            "Crucifixo Invertido": ItemAtivo(
                nome="Crucifixo Invertido",
                descricao="Aumenta seu dano temporariamente na sala atual",
                usos=2,
                efeitos=[
                    DanoUsuario(20, "+")
                ],
                afetaIni=False,
                sprite=image.load("assets\itens\ChapeuDeBruxa.png").convert_alpha(),
                raridade="comum",
                id=9,
            ),
            "Aranha de brinquedo": ItemAtivo(
                nome="Aranha de brinquedo",
                descricao="Aumenta sua velocidade nesta sala",
                usos=3,
                efeitos=[
                    VelocidadeMovimento(0.25)
                ],
                afetaIni=False,
                sprite=image.load("assets\itens\AranhaDeBrinquedo.png").convert_alpha(),
                raridade="comum",
                id=10,
            ),
            "Bomba": ItemAtivo(
                nome="Bomba",
                descricao="Dá dano em todos os inimigos nesta sala",
                usos=2,
                efeitos=[
                    DarDano(20)
                ],
                afetaIni=True,
                sprite=image.load("assets\itens\Bomba.png").convert_alpha(),
                raridade="comum",
                id=11,
            )

        }
        self.itens_por_id = {item.id: item for item in self.itens.values()}
