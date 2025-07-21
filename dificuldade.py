class Dificuldade:
    def __init__(self, nivel='normal'):
        self.set_dificuldade(nivel)

    def set_dificuldade(self, nivel):
        self.nivel = nivel
        if nivel == 'normal':
            self.mult_dano_jogador = 1.0
            self.mult_dano_inimigo = 1.0
            self.levas = 1
        elif nivel == 'dificil':
            self.mult_dano_jogador = 1.5
            self.mult_dano_inimigo = 0.5
            self.levas = 1
        elif nivel == 'criança da noite':
            self.mult_dano_jogador = 2.0
            self.mult_dano_inimigo = 0.3
            self.levas = 2
        elif nivel == 'lua de sangue':
            self.mult_dano_jogador = 3.0
            self.mult_dano_inimigo = 2
            self.levas = 3
        else:
            self.mult_dano_jogador = 1.0
            self.mult_dano_inimigo = 1.0
            self.levas = 3

    def chance(self, raridade):
        raridade = raridade.lower()
        chances = {
            'Normal': {
                'comum': 70,
                'incomum': 20,
                'raro': 7,
                'lendaria': 3
            },
            'Difícil': {
                'comum': 60,
                'incomum': 20,
                'raro': 7,
                'lendaria': 13
            },
            'Criança Da Noite': {
                'comum': 50,
                'incomum': 20,
                'raro': 7,
                'lendaria': 23
            },
            'Lua De Sangue': {
                'comum': 40,
                'incomum': 20,
                'raro': 7,
                'lendaria': 33
            }
        }

        dist = chances.get(self.nivel, chances['Normal'])
        return dist.get(raridade, 0)



dificuldade_global = Dificuldade('Normal')

