from ast import Mult
from pygame import *
import sys
from pygame.locals import QUIT
import math
from efeito import *
from random import randint
from utils import resource_path
from random import choice

class ConjuntoItens:
    def __init__(self):
        self.itens = {
            "Chapéu de bruxa": Item(
                nome="Chapéu de bruxa",
                descricao="Aumenta sua força",
                efeitos=[
                    AumentarForca(3),
                ],
                sprite=image.load(resource_path("assets\itens\ChapeuDeBruxa.png")).convert_alpha(),
                raridade="comum",
                id=1,
            ),
            "Botas de Sangue": Item(
                nome="Sapato de Sangue",
                descricao="Aumenta sua agilidade",
                efeitos=[
                    AumentarAgilidade(2)
                ],
                sprite=image.load(resource_path("assets\itens\Botasdesangue.png")).convert_alpha(),
                raridade="comum",
                id=2,
            ),
            "Luva de Titã": Item(
                nome="Luva de Titã",
                descricao="Aumenta sua destreza",
                efeitos=[
                    AumentarDestreza(3)
                ],
                sprite=image.load(resource_path("assets\itens\LuvaDeTita.png")).convert_alpha(),
                raridade="comum",
                id=3,
            ),
            "Seringa de Sangue": Item(
                nome="Seringa de Sangue",
                descricao="Aumenta seu vigor",
                efeitos=[
                    AumentarVigor(3)
                ],
                sprite=image.load(resource_path("assets\itens\SeringaDeSangue.png")).convert_alpha(),
                raridade="rara",
                id=4,
            ),
            "Cajado Mágico": Item(
                nome="Cajado Mágico",
                descricao="Aumenta sua força e sorte",
                efeitos=[
                    AumentarForca(2),
                    AumentarSorte(2)
                ],
                sprite=image.load(resource_path("assets\itens\Varinhamagica.png")).convert_alpha(),
                raridade="rara",
                id=5,
            ),
            "Água Benta": Item(
                nome="Água Benta",
                descricao="Aumenta muito sua força mas reduz vigor",
                efeitos=[
                    AumentarForca(5),
                    AumentarVigor(-2)
                ],
                sprite=image.load(resource_path("assets\itens\AguaBenta.png")).convert_alpha(),
                raridade="rara",
                id=6,
            ),
            "Coração Humano": Item(
                nome="Coração Humano",
                descricao="Aumenta vigor mas reduz força",
                efeitos=[
                    AumentarVigor(5),
                    AumentarForca(-2)
                ],
                sprite=image.load(resource_path("assets\itens\coração.png")).convert_alpha(),
                raridade="lendaria",
                id=7
            ),
            "Caixão do Papa Vamp": Item(
                nome="Caixão do Papa Vamp",
                descricao="Dá uma chance extra de reviver",
                efeitos=[
                    Revives(1)
                ],
                sprite=image.load(resource_path("assets\itens\caixao.png")).convert_alpha(),
                raridade="lendaria",
                id=8,
            ),
            "Máscara da Comédia": Item(
                nome="Máscara da Comédia",
                descricao="Aumenta levemente todos os atributos",
                efeitos=[
                    AumentarForca(1),
                    AumentarDestreza(1),
                    AumentarAgilidade(1),
                    AumentarVigor(1),
                    AumentarResistencia(1),
                    AumentarEstamina(1),
                    AumentarSorte(1)
                ],
                sprite=image.load(resource_path("assets\itens\Máscara_da_Comédia.png")).convert_alpha(),
                raridade="rara",
                id=9,
            ),
            "Máscara da Tragédia": Item(
                nome="Máscara da Tragédia",
                descricao="Aumenta muito a força mas reduz outros atributos",
                efeitos=[
                    AumentarForca(5),
                    AumentarDestreza(-1),
                    AumentarAgilidade(-1),
                    AumentarVigor(-1),
                    AumentarResistencia(-1),
                    AumentarEstamina(-1)
                ],
                sprite=image.load(resource_path("assets\itens\Máscara_da_Tragedia.png")).convert_alpha(),
                raridade="rara",
                id=10,
            ),
            "Amuleto de Seth": Item(
                nome="Amuleto de Seth",
                descricao="Aumenta um atributo aleatório",
                efeitos=[
                    choice([
                        AumentarForca(randint(1,3)),
                        AumentarDestreza(randint(1,3)),
                        AumentarAgilidade(randint(1,3)),
                        AumentarVigor(randint(1,3)),
                        AumentarResistencia(randint(1,3)),
                        AumentarEstamina(randint(1,3)),
                        AumentarSorte(randint(1,3))
                    ])
                ],
                sprite=image.load(resource_path("assets\itens\AmuletodeSeth.png")).convert_alpha(),
                raridade="comum",
                id=11
            ),
            "Anel do Rei Rato": Item(
                nome="Anel do Rei Rato",
                descricao="Aumenta estamina mas reduz força",
                efeitos=[
                    AumentarEstamina(3),
                    AumentarForca(-1)
                ],
                sprite=image.load(resource_path("assets\itens\AnelDoReiRato.png")).convert_alpha(),
                raridade="rara",
                id=12,
            ),
            "Escudo de Rubi": Item(
                nome="Escudo de Rubi",
                descricao="Aumenta resistência",
                efeitos=[
                    AumentarResistencia(3)
                ],
                sprite=image.load(resource_path("assets\itens\Escudo.png")).convert_alpha(),
                raridade="rara",
                id=13
            ),
            "Osso": Item(
                nome="Osso Frágil",
                descricao="Aumenta força mas reduz resistência",
                efeitos=[
                    AumentarForca(4),
                    AumentarResistencia(-2)
                ],
                sprite=image.load(resource_path("assets\itens\Osso.png")).convert_alpha(),
                raridade="lendaria",
                id=14
            ),
            "Sapatos Do Hermes": Item(
                nome="Sapatos Do Hermes",
                descricao="Aumenta muito agilidade e estamina",
                efeitos=[
                    AumentarAgilidade(4),
                    AumentarEstamina(3)
                ],
                sprite=image.load(resource_path("assets\itens\BotasdeHermes.png")).convert_alpha(),
                raridade="lendaria",
                id=15
            ),
            # Itens Ativos:
            "Crucifixo Invertido": ItemAtivo(
                nome="Crucifixo Invertido",
                descricao="Aumenta temporariamente sua força",
                usos=2,
                efeitos=[
                    AumentarForca(5)
                ],
                afetaIni=False,
                sprite=image.load(resource_path("assets\itens\crucifixoinvertido.png")).convert_alpha(),
                raridade="ativo",
                id=16,
            ),
            "Aranha de brinquedo": ItemAtivo(
                nome="Aranha de brinquedo",
                descricao="Aumenta temporariamente sua agilidade",
                usos=3,
                efeitos=[
                    AumentarAgilidade(3)
                ],
                afetaIni=False,
                sprite=image.load(resource_path("assets\itens\AranhaDeBrinquedo.png")).convert_alpha(),
                raridade="ativo",
                id=17,
            ),
            "Bomba": ItemAtivo(
                nome="Bomba",
                descricao="Causa dano em todos os inimigos",
                usos=2,
                efeitos=[
                    DarDano(20)
                ],
                afetaIni=True,
                sprite=image.load(resource_path("assets\itens\Bomba.png")).convert_alpha(),
                raridade="ativo",
                id=18,
            ),
            "Adaga Sangrenta": ItemAtivo(
                nome="Adaga Sangrenta",
                descricao="Aumenta dano recebido pelos inimigos",
                usos=2,
                efeitos=[
                    ModificadorDanoRecebido(2)
                ],
                afetaIni=True,
                sprite=image.load(resource_path("assets\itens\AdagaSangrenta.png")).convert_alpha(),
                raridade="ativo",
                id=19,
            )
        }
        self.itens_por_id = {item.id: item for item in self.itens.values()}