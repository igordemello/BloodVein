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
                    VelocidadeMovimento(0.3)
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
            "Cajado Mágico": Item(
                nome="Cajado Mágico",
                descricao="Aumenta o dano",
                efeitos=[
                    DanoUsuario(1.5, "*")
                ],
                sprite=image.load("assets\itens\Varinhamagica.png").convert_alpha(),
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
                nome="Coração Humano", #só entra em efeito depois do jogador tomar dano, corrigir
                descricao="Sua vida não decaí mais, mas ela é reduzida pela metade",
                efeitos=[
                    VidaMaxima(-50),
                    DecaimentoVida(0)
                ],
                sprite=image.load("assets\itens\coração.png").convert_alpha(),
                raridade="lendaria",
                id=7
            ),
            "Caixão do Papa Vamp": Item(
                nome="Caixão do Papa Vamp",
                descricao="Ao morrer, você revive uma vez",
                efeitos=[
                    Revives(1)
                ],
                sprite=image.load("assets\itens\caixao.png").convert_alpha(),
                raridade="lendaria",
                id=8,
            ),
            "Máscara da Comédia": Item(
                nome="Máscara da Comédia",
                descricao="Todos os seus status recebem um leve aumento",
                efeitos=[ #aumenta um pouco de tudo
                    DanoUsuario(10, "+"),
                    VidaMaxima(20),
                    VelocidadeAtaque(-0.2),
                    VelocidadeMovimento(0.1),
                    DecaimentoVida(0.75),
                    CooldownStamina(850),
                ],
                sprite=image.load("assets\itens\Máscara_da_Comédia.png").convert_alpha(),
                raridade="rara",
                id=9,
            ),
            "Máscara da Tragédia": Item(
                nome="Máscara da Tragédia",
                descricao="Diminui todos os status mas aumenta absurdamente sua força",
                efeitos=[ #diminui tudo mas aumenta o dano
                    DanoUsuario(75, "+"),
                    VidaMaxima(-15),
                    VelocidadeAtaque(-0.2),
                    VelocidadeMovimento(-0.1),
                    DecaimentoVida(1.4),
                    CooldownStamina(-850),
                ],
                sprite=image.load("assets\itens\Máscara_da_Tragedia.png").convert_alpha(),
                raridade="rara",
                id=10,
            ),
            "Amuleto de Seth" : Item(
                nome="Amuleto de Seth",
                descricao="Aumenta seu dano num valor aleatório quando obtido",
                efeitos=[
                    DanoUsuario(randint(1,35),"+")
                ],
                sprite=image.load("assets\itens\AmuletodeSeth.png").convert_alpha(),
                raridade="comum",
                id=11
            ),
            "Anel do Rei Rato" : Item(
                nome="Anel do Rei Rato",
                descricao="Diminui seu dano, mas também diminui o cooldown de recuperação\nde estamina",
                efeitos=[
                    CooldownStamina(2000),
                    DanoUsuario(-10,"+")
                ],
                sprite=image.load("assets\itens\AnelDoReiRato.png").convert_alpha(),
                raridade="rara",
                id=12,
            ),
            "Escudo de Rubi" : Item(
                nome="Escudo de Rubi",
                descricao="Diminui o dano que você recebe",
                efeitos=[
                    ModificadorDanoRecebido(0.75)
                ],
                sprite=image.load("assets\itens\Escudo.png").convert_alpha(),
                raridade="rara",
                id = 13
            ),
            "Osso" : Item(
                nome="Osso Frágil", #mudar o nome depois, tá muito basico
                descricao="Dobra o dano que você recebe, mas também dobra o dano que você dá",
                efeitos=[
                    ModificadorDanoRecebido(2),
                    DanoUsuario(2,"*")
                ],
                sprite=image.load("assets\itens\Osso.png").convert_alpha(),
                raridade="lendaria",
                id = 14
            ),
            "Sapatos Do Hermes" : Item(
                nome="Sapatos Do Hermes", 
                descricao="Super Dash",
                efeitos=[
                    CooldownStamina(900),
                    CooldownDash(100),
                    DuraçãoDash(180),
                    CustoDash(0.75)
                ],
                sprite=image.load("assets\itens\BotasdeHermes.png").convert_alpha(),
                raridade="lendaria",
                id = 15
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
                sprite=image.load("assets\itens\crucifixoinvertido.png").convert_alpha(),
                raridade="ativo",
                id=16,
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
                raridade="ativo",
                id=17,
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
                raridade="ativo",
                id=18,
            ),
            "Adaga Sangrenta": ItemAtivo(
                nome="Adaga Sangrenta",
                descricao="Quando ativado, aplica sangramento a todos os inimigo duplicando dano recebido",
                usos=2,
                efeitos=[
                    ModificadorDanoRecebido(2)
                ],
                afetaIni=True,
                sprite=image.load("assets\itens\AdagaSangrenta.png").convert_alpha(),
                raridade="ativo",
                id=19,
            )

        }
        self.itens_por_id = {item.id: item for item in self.itens.values()}
