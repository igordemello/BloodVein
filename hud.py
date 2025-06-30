from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font
from random import randint
from armas import *


class Hud:
    def __init__(self, player,tela):
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
        self.hud = image.load('assets/UI/Hud.png').convert_alpha()
        self.fundo = image.load('assets/UI/tela_fundo1.png').convert_alpha()
        self.fundo2 = image.load('assets/UI/tela_fundo2.jpeg').convert_alpha()

        self.statsArma = transform.scale(image.load('assets/UI/stats.png').convert_alpha(),(300*1.3,250*1.3))

        self.chanceCriticoTita= transform.scale(image.load('assets/UI/espadatitaCrit.png').convert_alpha(), (100,80))

        self.armaIcon = transform.scale(image.load(self.player.arma.spriteIcon).convert_alpha(), (96,96))

        self.fundo = transform.scale(self.fundo, (1920, 1080))

        self.stats_alpha = None

        # Variáveis para o efeito de shake
        self.combo_shake_intensity = 0
        self.combo_shake_duration = 0
        self.last_combo_count = 0
        self.shake_offset = (0, 0)
        self.combo_scale = 1.0
        self.normal_font_size = 96
        self.enlarged_font_size = 110

        self.tela = tela

    def desenhaFundo(self):
        self.tela.blit(self.fundo, (0, 0))

    def desenhaFundo2(self):
        self.tela.blit(self.fundo2, (0,0))

    def update(self, dt):
        if self.combo_shake_duration > 0:
            self.combo_shake_duration -= dt
            intensity = int(self.combo_shake_intensity * (self.combo_shake_duration / 300))
            self.shake_offset = (
                randint(-intensity, intensity) if intensity > 0 else 0,
                randint(-intensity, intensity) if intensity > 0 else 0
            )
            self.combo_scale = 1.0 + (0.2 * (self.combo_shake_duration / 300))
        else:
            self.shake_offset = (0, 0)
            self.combo_scale = 1.0

        total_hits = self.player.hits + self.player.hits_projetil
        if total_hits > self.last_combo_count:
            self.trigger_combo_shake()
        self.last_combo_count = total_hits
        if hasattr(self, 'arma_anterior') and self.arma_anterior != self.player.arma:
            self.atualizar_arma_icon()
        self.arma_anterior = self.player.arma

    def trigger_combo_shake(self):
        self.combo_shake_intensity = min(10 + self.player.hits * 0.5, 30)
        self.combo_shake_duration = 300

    def desenhar(self):
        almas_font = font.Font('assets/Fontes/alagard.ttf', 48)
        almas = almas_font.render(f"{self.player.almas}x", True, (243, 236, 215))

        total_hits = self.player.hits + self.player.hits_projetil
        combo_mult = self.player.arma.comboMult

        current_font_size = int(self.normal_font_size * self.combo_scale)
        combo_font = font.Font('assets/Fontes/alagard.ttf',
                               max(72, min(int(current_font_size * combo_mult * 0.6), 165)))
        combo = combo_font.render(f"{total_hits}", True, (243, 236, 215))

        comboMult_font = font.Font('assets/Fontes/alagard.ttf', min(int(24 * combo_mult), 48))
        comboMult = comboMult_font.render(f"{combo_mult:.2f}x", True, (253, 246, 225))


        almas_rect = almas.get_rect()
        almas_rect.right = 1540
        almas_rect.top = 68

        base_combo_rect = combo.get_rect()
        base_combo_rect.right = 1880
        base_combo_rect.top = 200

        combo_rect = combo.get_rect()
        combo_rect.right = 1880 + self.shake_offset[0]
        combo_rect.top = 190 + self.shake_offset[1]

        comboMult_rect = comboMult.get_rect()
        comboMult_rect.centerx = base_combo_rect.centerx + self.shake_offset[0] * 0.7
        comboMult_rect.top = base_combo_rect.bottom - 15 + self.shake_offset[1] * 0.7


        self.tela.blit(self.hud, (0, 0))

        # HP Bar
        larguraHp_total = self.bracoHp_cima.get_width()
        alturaHp_total = self.bracoHp_cima.get_height() - 100
        proporcaoHp = max(0, min(1, self.player.hp / 100))
        altura_visivelHp = int(alturaHp_total * proporcaoHp)

        self.tela.blit(self.bracoHp_fundo, (15, 510))

        if altura_visivelHp > 0:
            y_corte = self.bracoHp_cima.get_height() - altura_visivelHp
            barra_cheia_cortada = self.bracoHp_cima.subsurface((0, y_corte, larguraHp_total, altura_visivelHp)).copy()
            self.tela.blit(barra_cheia_cortada, (15, 510 + y_corte))

        # Desenha itens
        for i, (item, qtd) in enumerate(self.player.itens.items()):
            x = 200 + (i % 6) * 75
            y = 25 + (i // 6) * 64
            sprite = transform.scale(item.sprite, (64, 64))
            self.tela.blit(sprite, (x, y))

        # Itens ativos
        if self.player.itemAtivo is not None:
            for x in range(0, self.player.itemAtivo.usos):
                draw.rect(self.tela, (0, 255, 0), (50 + (x * 25), 144, 20, 8))
            sprite = transform.scale(self.player.itemAtivo.sprite, (96, 96))
            self.tela.blit(sprite, (60, 40))

        # Almas
        self.tela.blit(self.almaIcon, (1545, 33))
        self.tela.blit(almas, almas_rect)

        self.tela.blit(self.armaIcon, (1710, 48))

        #Se espada do titã, mostra chance critico:
        if isinstance(self.player.arma, EspadaDoTita):
            crit_font = font.Font('assets/Fontes/alagard.ttf', 36)
            critico = crit_font.render(f"{self.player.arma.chanceCritico}%", True, (243, 236, 215))
            crit_rect = critico.get_rect()
            crit_rect.right = 1795
            crit_rect.top = 170

            self.tela.blit(self.chanceCriticoTita, (1710,150,110,74))
            self.tela.blit(critico, (crit_rect))

        if total_hits > 0:
            self.tela.blit(combo, combo_rect.topleft)
            self.tela.blit(comboMult, comboMult_rect.topleft)


        # Stamina Bar
        braco_stamina = self.bracoSt_fundo
        larguraSt_total = self.bracoSt_cima.get_width()
        alturaSt_total = self.bracoSt_cima.get_height() - 70
        proporcaoSt = max(0, min(1, self.player.st / 100))
        altura_visivelSt = int(alturaSt_total * proporcaoSt)

        self.tela.blit(braco_stamina, (1715, 510))

        if altura_visivelSt > 0:
            y_corte = self.bracoSt_cima.get_height() - altura_visivelSt
            barra_cheia_cortada = self.bracoSt_cima.subsurface((0, y_corte, larguraSt_total, altura_visivelSt)).copy()
            self.tela.blit(barra_cheia_cortada, (1715, 510 + y_corte))

    def atualizar_arma_icon(self):
        self.armaIcon = transform.scale(image.load(self.player.arma.spriteIcon).convert_alpha(), (96, 96))

    def mostraStatsArma(self, arma_atual):
        if not hasattr(self, 'stats_alpha'):
            self.stats_alpha = 0
        else:
            self.stats_alpha = min(self.stats_alpha + 20, 255)

        dano = arma_atual.dano
        rapidez = arma_atual.velocidade
        roubo_de_vida = arma_atual.lifeSteal
        chance_de_critico = arma_atual.chanceCritico
        dano_critico = arma_atual.dano * arma_atual.danoCriticoMod
        modificador = arma_atual.modificador.nome

        stats_font = font.Font('assets/Fontes/alagard.ttf', 24)

        stats_surface = Surface((400, 300), SRCALPHA)

        self.statsArma.set_alpha(self.stats_alpha)
        stats_surface.blit(self.statsArma, (0, 0))

        texts = [
            stats_font.render(f"Dano: {dano}", True, (243, 236, 215)),
            stats_font.render(f"Rapidez: {rapidez}", True, (243, 236, 215)),
            stats_font.render(f"Roubo de Vida: {roubo_de_vida}", True, (243, 236, 215)),
            stats_font.render(f"Chance de Critico: {chance_de_critico}%", True, (243, 236, 215)),
            stats_font.render(f"Dano Critico: {dano_critico}", True, (243, 236, 215)),
            stats_font.render(f"Modificador: {modificador}", True, (243, 236, 215))
        ]

        for i, text in enumerate(texts):
            text.set_alpha(self.stats_alpha)
            stats_surface.blit(text, (45, 55 + i * 42))

        self.tela.blit(stats_surface, (770, 750))

    def reset_stats_fade(self):
        self.stats_alpha = 0
