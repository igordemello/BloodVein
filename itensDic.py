from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *
from random import randint

class ConjuntoItens:
    def __init__(self):
        self.itens = {
            "Witch Hat": Item(
                nome="Witch Hat",
                descricao="Increases your damage",
                efeitos=[
                    DanoUsuario(20, "+"),
                ],
                sprite=image.load("assets/itens/ChapeuDeBruxa.png").convert_alpha(),
                raridade="comum",
                id=1,
            ),
            "Blood Shoes": Item(
                nome="Blood Shoes",
                descricao="Increases your speed",
                efeitos=[
                    VelocidadeMovimento(0.3)
                ],
                sprite=image.load("assets/itens/Botasdesangue.png").convert_alpha(),
                raridade="comum",
                id=2,
            ),
            "Titan Glove": Item(
                nome="Titan Glove",
                descricao="Decreases attack duration",
                efeitos=[
                    VelocidadeAtaque(1)
                ],
                sprite=image.load("assets/itens/LuvaDeTita.png").convert_alpha(),
                raridade="comum",
                id=3,
            ),
            "Blood Syringe": Item(
                nome="Blood Syringe",
                descricao="Reduces health decay",
                efeitos=[
                    DecaimentoVida(0.75)
                ],
                sprite=image.load("assets/itens/SeringaDeSangue.png").convert_alpha(),
                raridade="rara",
                id=4,
            ),
            "Magic Staff": Item(
                nome="Magic Staff",
                descricao="Increases damage",
                efeitos=[
                    DanoUsuario(1.5, "*")
                ],
                sprite=image.load("assets/itens/Varinhamagica.png").convert_alpha(),
                raridade="rara",
                id=5,
            ),
            "Holy Water": Item(
                nome="Holy Water",
                descricao="Doubles health decay and doubles your damage",
                efeitos=[
                    DanoUsuario(2, "*"),
                    DecaimentoVida(2)
                ],
                sprite=image.load("assets/itens/AguaBenta.png").convert_alpha(),
                raridade="rara",
                id=6,
            ),
            "Human Heart": Item(
                nome="Human Heart",
                descricao="Your health no longer decays, but it's halved",
                efeitos=[
                    VidaMaxima(-50),
                    DecaimentoVida(0)
                ],
                sprite=image.load("assets/itens/ChapeuDeBruxa.png").convert_alpha(),
                raridade="lendaria",
                id=7
            ),
            "Vamp Pope's Coffin": Item(
                nome="Vamp Pope's Coffin",
                descricao="When you die, you revive once",
                efeitos=[
                    Revives(1)
                ],
                sprite=image.load("assets/itens/ChapeuDeBruxa.png").convert_alpha(),
                raridade="lendaria",
                id=8,
            ),
            "Comedy Mask": Item(
                nome="Comedy Mask",
                descricao="All your stats get a small boost",
                efeitos=[
                    DanoUsuario(10, "+"),
                    VidaMaxima(20),
                    VelocidadeAtaque(-0.2),
                    VelocidadeMovimento(0.1),
                    DecaimentoVida(0.75),
                    CooldownStamina(850),
                ],
                sprite=image.load("assets/itens/Máscara_da_Comédia.png").convert_alpha(),
                raridade="rara",
                id=9,
            ),
            "Tragedy Mask": Item(
                nome="Tragedy Mask",
                descricao="Decreases all stats but greatly increases your strength",
                efeitos=[
                    DanoUsuario(75, "+"),
                    VidaMaxima(-15),
                    VelocidadeAtaque(-0.2),
                    VelocidadeMovimento(-0.1),
                    DecaimentoVida(1.4),
                    CooldownStamina(-850),
                ],
                sprite=image.load("assets/itens/Máscara_da_Tragedia.png").convert_alpha(),
                raridade="rara",
                id=10,
            ),
            "Seth's Amulet": Item(
                nome="Seth's Amulet",
                descricao="Increases your damage by a random amount when obtained",
                efeitos=[
                    DanoUsuario(randint(1, 35), "+")
                ],
                sprite=image.load("assets/itens/AmuletodeSeth.png").convert_alpha(),
                raridade="comum",
                id=11
            ),
            "Rat King's Ring": Item(
                nome="Rat King's Ring",
                descricao="Reduces your damage, but also reduces stamina recovery cooldown",
                efeitos=[
                    CooldownStamina(2000),
                    DanoUsuario(-10, "+")
                ],
                sprite=image.load("assets/itens/AnelDoReiRato.png").convert_alpha(),
                raridade="rara",
                id=12,
            ),
            "Ruby Shield": Item(
                nome="Ruby Shield",
                descricao="Reduces the damage you take",
                efeitos=[
                    ModificadorDanoRecebido(0.75)
                ],
                sprite=image.load("assets/itens/Escudo.png").convert_alpha(),
                raridade="rara",
                id=13
            ),
            "Fragile Bone": Item(
                nome="Fragile Bone",
                descricao="Doubles the damage you take, but also doubles the damage you deal",
                efeitos=[
                    ModificadorDanoRecebido(2),
                    DanoUsuario(2, "*")
                ],
                sprite=image.load("assets/itens/Osso.png").convert_alpha(),
                raridade="lendaria",
                id=14
            ),
            "Hermes' Shoes": Item(
                nome="Hermes' Shoes",
                descricao="Super Dash",
                efeitos=[
                    CooldownStamina(900),
                    CooldownDash(100),
                    DuraçãoDash(180),
                    CustoDash(0.75)
                ],
                sprite=image.load("assets/itens/BotasdeHermes.png").convert_alpha(),
                raridade="lendaria",
                id=15
            ),
            # Active Items:
            "Inverted Crucifix": ItemAtivo(
                nome="Inverted Crucifix",
                descricao="Temporarily increases your damage in the current room",
                usos=2,
                efeitos=[
                    DanoUsuario(20, "+")
                ],
                afetaIni=False,
                sprite=image.load("assets/itens/crucifixoinvertido.png").convert_alpha(),
                raridade="comum",
                id=16,
            ),
            "Toy Spider": ItemAtivo(
                nome="Toy Spider",
                descricao="Increases your speed in this room",
                usos=3,
                efeitos=[
                    VelocidadeMovimento(0.25)
                ],
                afetaIni=False,
                sprite=image.load("assets/itens/AranhaDeBrinquedo.png").convert_alpha(),
                raridade="comum",
                id=17,
            ),
            "Bomb": ItemAtivo(
                nome="Bomb",
                descricao="Deals damage to all enemies in this room",
                usos=2,
                efeitos=[
                    DarDano(20)
                ],
                afetaIni=True,
                sprite=image.load("assets/itens/Bomba.png").convert_alpha(),
                raridade="comum",
                id=18,
            ),
            "Bloody Dagger": ItemAtivo(
                nome="Bloody Dagger",
                descricao="When activated, applies bleeding to all enemies\ndoubling the damage they take",
                usos=2,
                efeitos=[
                    ModificadorDanoRecebido(2)
                ],
                afetaIni=True,
                sprite=image.load("assets/itens/AdagaSangrenta.png").convert_alpha(),
                raridade="comum",
                id=19,
            )
        }
        self.itens_por_id = {item.id: item for item in self.itens.values()}