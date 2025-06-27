from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font
from random import randint


class Hud:
    def __init__(self, player):
        self.player = player
        self.bracoHp_fundo = transform.scale(image.load('assets/UI/HDEmptyHealthUI - Rotacionada.png').convert_alpha(),
                                             (192, 576))
        self.bracoHp_cima = transform.scale(image.load('assets/UI/HDFillHealthUI - Rotacionada.png').convert_alpha(),
                                            (192, 576))
        self.bracoSt_fundo = transform.flip(
            transform.scale(image.load('assets/UI/HDEmptyManaUI - Rotacionada.png').convert_alpha(), (192, 576)), True,
            False)
        self.bracoSt_cima = transform.flip(
            transform.scale(image.load('assets/UI/HDFillManaUI - Rotacionada.png').convert_alpha(), (192, 576)), True,
            False)

        self.almaIcon = transform.scale(image.load('assets/Itens/alma.png').convert_alpha(), (96, 96))
        self.hud = image.load('assets/UI/Hud.png')
        self.fundo = image.load('assets/UI/tela_fundo1.png')
        self.fundo = transform.scale(self.fundo, (1920, 1080))

        # Variáveis para o efeito de shake
        self.combo_shake_intensity = 0
        self.combo_shake_duration = 0
        self.last_combo_count = 0
        self.shake_offset = (0, 0)
        self.combo_scale = 1.0
        self.normal_font_size = 96
        self.enlarged_font_size = 110

    def desenhaFundo(self, tela):
        tela.blit(self.fundo, (0, 0))

    def update(self, dt):
        # Atualiza o efeito de shake
        if self.combo_shake_duration > 0:
            self.combo_shake_duration -= dt
            intensity = int(self.combo_shake_intensity * (self.combo_shake_duration / 300))  # Convertemos para int
            self.shake_offset = (
                randint(-intensity, intensity) if intensity > 0 else 0,
                randint(-intensity, intensity) if intensity > 0 else 0
            )
            self.combo_scale = 1.0 + (0.2 * (self.combo_shake_duration / 300))
        else:
            self.shake_offset = (0, 0)
            self.combo_scale = 1.0

        # Detecta quando o combo aumenta
        if self.player.hits > self.last_combo_count:
            self.trigger_combo_shake()
        self.last_combo_count = self.player.hits

    def trigger_combo_shake(self):
        """Inicia o efeito de shake quando o combo aumenta"""
        self.combo_shake_intensity = min(10 + self.player.hits * 0.5, 30)
        self.combo_shake_duration = 300

    def desenhar(self, tela):
        almas_font = font.Font('assets/Fontes/alagard.ttf', 48)
        almas = almas_font.render(f"{self.player.almas}x", True, (243, 236, 215))

        # Fontes para o combo (tamanho varia com o shake)
        current_font_size = int(self.normal_font_size * self.combo_scale)
        combo_font = font.Font('assets/Fontes/alagard.ttf', max(72, min(int(current_font_size * self.player.arma.comboMult * 0.6), 165)))
        combo = combo_font.render(f"{self.player.hits}", True, (243, 236, 215))

        comboMult_font = font.Font('assets/Fontes/alagard.ttf',  min(int(24 * self.player.arma.comboMult), 48))
        comboMult = comboMult_font.render(f"{self.player.arma.comboMult:.2f}x", True, (253, 246, 225))

        almas_rect = almas.get_rect()
        almas_rect.right = 1700
        almas_rect.top = 58

        # Posição original do combo (sem shake)
        base_combo_rect = combo.get_rect()
        base_combo_rect.right = 1880
        base_combo_rect.top = 200

        # Aplica efeitos de shake e scale
        combo_rect = combo.get_rect()
        combo_rect.right = 1880 + self.shake_offset[0]
        combo_rect.top = 190 + self.shake_offset[1]

        comboMult_rect = comboMult.get_rect()
        comboMult_rect.centerx = base_combo_rect.centerx + self.shake_offset[0] * 0.7
        comboMult_rect.top = base_combo_rect.bottom - 15 + self.shake_offset[1] * 0.7


        tela.blit(self.hud, (0, 0))

        # HP Bar
        larguraHp_total = self.bracoHp_cima.get_width()
        alturaHp_total = self.bracoHp_cima.get_height() - 100
        proporcaoHp = max(0, min(1, self.player.hp / 100))
        altura_visivelHp = int(alturaHp_total * proporcaoHp)

        tela.blit(self.bracoHp_fundo, (15, 510))

        if altura_visivelHp > 0:
            y_corte = self.bracoHp_cima.get_height() - altura_visivelHp
            barra_cheia_cortada = self.bracoHp_cima.subsurface((0, y_corte, larguraHp_total, altura_visivelHp)).copy()
            tela.blit(barra_cheia_cortada, (15, 510 + y_corte))

        # Desenha itens
        for i, (item, qtd) in enumerate(self.player.itens.items()):
            x = 200 + (i % 6) * 75
            y = 25 + (i // 6) * 64
            sprite = transform.scale(item.sprite, (64, 64))
            tela.blit(sprite, (x, y))

        # Itens ativos
        if self.player.itemAtivo is not None:
            for x in range(0, self.player.itemAtivo.usos):
                draw.rect(tela, (0, 255, 0), (50 + (x * 25), 144, 20, 8))
            sprite = transform.scale(self.player.itemAtivo.sprite, (96, 96))
            tela.blit(sprite, (60, 40))

        # Almas
        tela.blit(self.almaIcon, (1710, 33))
        tela.blit(almas, almas_rect)

        # Combo (com efeitos)
        if self.player.hits > 0:
            tela.blit(combo, combo_rect.topleft)
            tela.blit(comboMult, comboMult_rect.topleft)

        # Stamina Bar
        braco_stamina = self.bracoSt_fundo
        larguraSt_total = self.bracoSt_cima.get_width()
        alturaSt_total = self.bracoSt_cima.get_height() - 70
        proporcaoSt = max(0, min(1, self.player.st / 100))
        altura_visivelSt = int(alturaSt_total * proporcaoSt)

        tela.blit(braco_stamina, (1715, 510))

        if altura_visivelSt > 0:
            y_corte = self.bracoSt_cima.get_height() - altura_visivelSt
            barra_cheia_cortada = self.bracoSt_cima.subsurface((0, y_corte, larguraSt_total, altura_visivelSt)).copy()
            tela.blit(barra_cheia_cortada, (1715, 510 + y_corte))