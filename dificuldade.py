class Dificuldade:
    def __init__(self, nivel='normal'):
        self.set_dificuldade(nivel)

    def set_dificuldade(self, nivel):
        self.nivel = nivel
        if nivel == 'normal':
            self.mult_dano_jogador = 1.2
            self.mult_dano_inimigo = 0.8
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
            self.mult_dano_inimigo = 0.1
            self.levas = 3
        else:
            self.mult_dano_jogador = 1.0
            self.mult_dano_inimigo = 1.0
            self.levas = 3

    def chance(self, raridade):
        raridade = raridade.lower()
        chances = {
            'Normal': {
                'comum': 85,  # Aumentado de 70
                'incomum': 10,  # Reduzido de 20
                'raro': 4,  # Reduzido de 7
                'lendaria': 1  # Reduzido de 3
            },
            'Difícil': {
                'comum': 75,  # Aumentado de 60
                'incomum': 15,  # Reduzido de 20
                'raro': 7,  # Mantido igual
                'lendaria': 3  # Reduzido de 13
            },
            'Criança Da Noite': {
                'comum': 65,  # Aumentado de 50
                'incomum': 15,  # Reduzido de 20
                'raro': 10,  # Aumentado de 7
                'lendaria': 10  # Reduzido de 23
            },
            'Lua De Sangue': {
                'comum': 55,  # Aumentado de 40
                'incomum': 15,  # Reduzido de 20
                'raro': 15,  # Aumentado de 7
                'lendaria': 15  # Reduzido de 33
            }
        }

        dist = chances.get(self.nivel, chances['Normal'])
        return dist.get(raridade, 0)



dificuldade_global = Dificuldade('Normal')

