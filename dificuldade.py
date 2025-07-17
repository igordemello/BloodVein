class Dificuldade:
    def __init__(self, nivel='normal'):
        self.set_dificuldade(nivel)

    def set_dificuldade(self, nivel):
        self.nivel = nivel
        if nivel == 'normal':
            self.mult_dano_jogador = 1.0
            self.mult_dano_inimigo = 1.0
        elif nivel == 'dificil':
            self.mult_dano_jogador = 1.5
            self.mult_dano_inimigo = 0.5
        elif nivel == 'criança da noite':
            self.mult_dano_jogador = 2.0
            self.mult_dano_inimigo = 0.25
        else:
            self.mult_dano_jogador = 1.0
            self.mult_dano_inimigo = 1.0

dificuldade_global = Dificuldade('criança da noite')
