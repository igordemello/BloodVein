from pygame import *

class Habilidade:
    def __init__(self, nome, custo, requisitos=[], requisito_alternativo=False,
                 descricao="", sprite_path=None):
        self.nome = nome
        self.custo = custo
        self.requisitos = requisitos
        self.requisito_alternativo = requisito_alternativo
        self.descricao = descricao
        self.sprite_path = sprite_path
        self.sprite = None


class GerenciadorHabilidades:
    def __init__(self):
        self.habilidades = {
            "Bola de Fogo": Habilidade("Bola de Fogo", 1),
            "Fonte Arcana": Habilidade("Fonte Arcana", 1),
            "Clarão": Habilidade("Clarão", 1, ["Bola de Fogo"]),
            "Nevasca": Habilidade("Nevasca", 1, ["Bola de Fogo"]),
            "Trovão": Habilidade("Trovão", 2, ["Clarão"]),
            "Núvem de Veneno": Habilidade("Núvem de Veneno", 2, ["Nevasca"]),
            "Escudo": Habilidade("Escudo", 2, ["Fonte Arcana"]),
            "Corrente Elétrica": Habilidade("Corrente Elétrica", 3, ["Trovão", "Núvem de Veneno"], True),
            "Eficiência Arcana": Habilidade("Eficiência Arcana", 3, ["Escudo"]),
            "Estomago de Mana": Habilidade("Estomago de Mana", 3, ["Escudo"]),
        }
        self.cor_disponivel = (100, 255, 100, 160)  # Verde
        self.cor_indisponivel = (150, 150, 150, 160)  # Cinza
        self.cor_desbloqueada = (200, 200, 200, 160)  # Cinza claro para habilidades já desbloqueadas

    def get_cor_botao(self, player, nome_habilidade):
        if nome_habilidade in player.habilidades:
            return self.cor_desbloqueada
        elif self.pode_desbloquear(player, nome_habilidade):
            return self.cor_disponivel
        else:
            return self.cor_indisponivel

    def pode_desbloquear(self, player, nome_habilidade):
        if nome_habilidade not in self.habilidades:
            return False

        hab = self.habilidades[nome_habilidade]

        if hab.nome in player.habilidades:
            return False

        if player.pontosHabilidade < hab.custo:
            return False

        if hab.requisito_alternativo:
            return any(req in player.habilidades for req in hab.requisitos)
        else:
            return all(req in player.habilidades for req in hab.requisitos)

    def desbloquear(self, player, nome_habilidade):
        if self.pode_desbloquear(player, nome_habilidade):
            player.habilidades.append(nome_habilidade)
            player.pontosHabilidade -= self.habilidades[nome_habilidade].custo
            return True
        return False