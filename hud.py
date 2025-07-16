from pygame import *
import sys
from pygame.locals import QUIT
import math
import pygame.font
from random import randint
from armas import *
from screen_shake import screen_shaker


class Hud:
    def __init__(self, player,tela):
        self.player = player
        
        self.fundo = image.load('assets/UI/tela_fundo1.png').convert_alpha()
        self.fundo = transform.scale(self.fundo, (1920, 1080))

        self.hud = image.load('assets/UI/HUD.png').convert_alpha()
        self.hud = transform.scale(self.hud, (self.hud.get_width()*0.9, self.hud.get_height()*0.9))

        self.full_stamina_mana = image.load('assets/UI/full_stamina_mana.png').convert_alpha()
        self.full_stamina_mana = transform.scale(self.full_stamina_mana, (self.full_stamina_mana.get_width()*0.9, self.full_stamina_mana.get_height()*0.9))

        self.full_hp = image.load('assets/UI/full_hp.png').convert_alpha()
        self.full_hp = transform.scale(self.full_hp, (self.full_hp.get_width()*0.9, self.full_hp.get_height()*0.9))

        self.pocoesHp = transform.scale(image.load('assets/itens/pocaodevida.png').convert_alpha(),(64,64))
        self.pocoesMp = transform.scale(image.load('assets/itens/pocaodemana.png').convert_alpha(),(64,64))

        self.almaIcon = transform.scale(image.load('assets/Itens/alma.png').convert_alpha(), (76,76))
        
        self.statsArma = transform.scale(image.load('assets/UI/stats.png').convert_alpha(),(300*1.3,250*1.3))
        
        self.stats_alpha = None


        #hotbar - temporária
        self.hotkeys_bg = Surface((400, 60), SRCALPHA)
        self.hotkeys_bg.fill((0, 0, 0, 150))
        self.hotkey_slots = [
            {"rect": Rect(50, 320 + i * 125, 100, 100), "color": (100, 100, 100, 200)}
            for i in range(4)
        ]
        self.hotkey_font = font.Font('assets/Fontes/alagard.ttf', 20)

        self.combo_shake_intensity = 0
        self.combo_shake_duration = 0
        self.last_combo_count = 0
        self.shake_offset = (0, 0)
        self.combo_scale = 1.0
        self.normal_font_size = 96
        self.enlarged_font_size = 110

        self.stats_alpha = None

        self.tela = tela

        # Mensagens temporárias
        self.mensagem_sem_stamina = False
        self.mensagem_sem_mana = False
        self.tempo_mensagem_stamina = 0
        self.tempo_mensagem_mana = 0
        self.duracao_mensagem = 1000

    def desenhaFundo(self):
        self.tela.blit(self.fundo, (0, 0))

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

        # Atualiza mensagens temporárias
        current_time = time.get_ticks()
        if self.mensagem_sem_stamina and current_time - self.tempo_mensagem_stamina > self.duracao_mensagem:
            self.mensagem_sem_stamina = False
        if self.mensagem_sem_mana and current_time - self.tempo_mensagem_mana > self.duracao_mensagem:
            self.mensagem_sem_mana = False

    def trigger_combo_shake(self):
        self.combo_shake_intensity = min(10 + self.player.hits * 0.5, 30)
        self.combo_shake_duration = 300

    def desenhar(self, minimal=False):
        offset_x, offset_y = screen_shaker.offset
        almas_font = font.Font('assets/Fontes/alagard.ttf', 55)
        almas = almas_font.render(f"{self.player.almas}x", True, (243, 236, 215))

        pocoes_font = font.Font('assets/Fontes/alagard.ttf', 32)

        pocao_slot_size = 100
        pocao_slots = [
            {"rect": Rect(50, 925, pocao_slot_size, pocao_slot_size), "tecla": "C", "pocao": self.pocoesHp,
             "qtd": self.player.pocoesHp, "color": (100, 100, 100, 200)},
            {"rect": Rect(170, 925, pocao_slot_size, pocao_slot_size), "tecla": "V", "pocao": self.pocoesMp,
             "qtd": self.player.pocoesMp, "color": (100, 100, 100, 200)}
        ]

        total_hits = self.player.hits + self.player.hits_projetil
        combo_mult = self.player.arma.comboMult

        current_font_size = int(self.normal_font_size * self.combo_scale)
        combo_font = font.Font('assets/Fontes/alagard.ttf',
                               max(72, min(int(current_font_size * combo_mult * 0.6), 165)))
        combo = combo_font.render(f"{total_hits}", True, (243, 236, 215))

        comboMult_font = font.Font('assets/Fontes/alagard.ttf', min(int(24 * combo_mult), 48))
        comboMult = comboMult_font.render(f"{combo_mult:.2f}x", True, (253, 246, 225))

        almas_rect = almas.get_rect()
        almas_rect.right = 1830
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

        if minimal:
            return

        #pocoes
        for slot in pocao_slots:
            slot_surface = Surface((slot["rect"].width, slot["rect"].height), SRCALPHA)
            slot_surface.fill(slot["color"])
            draw.rect(slot_surface, (255, 255, 255, 150), slot_surface.get_rect(), 2)
            self.tela.blit(slot_surface, (slot["rect"].x + offset_x, slot["rect"].y + offset_y))

            tecla_texto = self.hotkey_font.render(slot["tecla"], True, (243, 236, 215))
            self.tela.blit(tecla_texto, (slot["rect"].x + 45 + offset_x, slot["rect"].y - 20 + offset_y))

            pocao_img = slot["pocao"]
            img_rect = pocao_img.get_rect(center=slot["rect"].center)
            self.tela.blit(pocao_img, (img_rect.x + offset_x, img_rect.y + offset_y))

            qtd_text = pocoes_font.render(f"{slot['qtd']}x", True, (243, 236, 215))
            self.tela.blit(qtd_text, (slot["rect"].right - 65 + offset_x, slot["rect"].bottom + 5 + offset_y))

        #braços e coração fundo
        meio = self.tela.get_width() // 2
        x_hud = meio - self.hud.get_width() // 2

        self.tela.blit(self.hud, (x_hud, 885))


        #braços e coracao dinamico
        alturaHp_total = self.full_hp.get_height()
        proporcaoHp = max(0, min(1, self.player.hp / self.player.hpMax))
        altura_visivelHp = int(alturaHp_total * proporcaoHp)

        if altura_visivelHp > 0:
            y_corte = self.full_hp.get_height() - altura_visivelHp
            barra_cheia_cortada = self.full_hp.subsurface((0, y_corte, self.full_hp.get_width(), altura_visivelHp)).copy()
            self.tela.blit(barra_cheia_cortada, (x_hud, 885 + y_corte))
            # draw.rect(self.tela, (255, 0, 0), (x_hud, 885 + y_corte, self.full_hp.get_width(), altura_visivelHp), 2)


        largura_barra = 354
        margem = 60
        y_barra = 885

        proporcao_mana = max(0, min(1, self.player.mp / self.player.mpMaximo))
        proporcao_stamina = max(0, min(1, self.player.stamina / self.player.staminaMaximo))

        if proporcao_mana > 0:
            largura_visivel_mana = int(largura_barra * proporcao_mana)
            x_inicial_mana = margem + (largura_barra - largura_visivel_mana)
            barra_mana = self.full_stamina_mana.subsurface(
                (x_inicial_mana, 0, largura_visivel_mana, self.full_stamina_mana.get_height())
            ).copy()
            self.tela.blit(barra_mana, (x_hud + x_inicial_mana, y_barra))

        if proporcao_stamina > 0:
            largura_visivel_stamina = int(largura_barra * proporcao_stamina)
            x_inicio_stamina = self.full_stamina_mana.get_width() - margem - largura_barra
            barra_stamina = self.full_stamina_mana.subsurface(
                (x_inicio_stamina, 0, largura_visivel_stamina, self.full_stamina_mana.get_height())
            ).copy()
            self.tela.blit(barra_stamina, (x_hud + x_inicio_stamina, y_barra))


        #item ativo
        margem_item_x = 1625
        margem_item_y = 925

        if self.player.itemAtivo is not None:
            for x in range(self.player.itemAtivo.usos):
                draw.rect(self.tela, (0, 255, 0), (margem_item_x + (x * 25), margem_item_y + 104, 20, 8))

            sprite = transform.scale(self.player.itemAtivo.sprite, (96, 96))
            self.tela.blit(sprite, (margem_item_x + 10, margem_item_y))



        # Almas
        self.tela.blit(self.almaIcon, (almas_rect.right, 43))
        self.tela.blit(almas, almas_rect)

        #legenda hud
        hp_text = self.hotkey_font.render(f'{self.player.hp if self.player.hp > 0 else 0 :.0f}/{self.player.hpMax:.0f}', True, (243, 236, 215))
        mp_text = self.hotkey_font.render(f'{self.player.mp if self.player.mp > 0 else 0 :.0f}/{self.player.mpMaximo:.0f}', True, (243, 236, 215))
        stamina_text = self.hotkey_font.render(f'{self.player.stamina if self.player.stamina > 0 else 0 :.0f}/{self.player.staminaMaximo:.0f}', True, (243, 236, 215))

        legendas_y = 1020
        self.tela.blit(hp_text, (1025,legendas_y))
        self.tela.blit(mp_text, (550, legendas_y))
        self.tela.blit(stamina_text, (1300, legendas_y))

        if self.mensagem_sem_stamina:
            sem_stamina = self.hotkey_font.render('SEM STAMINA!', True, (243, 236, 215))
            self.tela.blit(sem_stamina, (1175, 925))

        if self.mensagem_sem_mana:
            sem_mana = self.hotkey_font.render('SEM MANA!', True, (243, 236, 215))
            self.tela.blit(sem_mana, (650, 925))




        if total_hits > 0:
            self.tela.blit(combo, combo_rect.topleft)
            self.tela.blit(comboMult, comboMult_rect.topleft)

        self.desenhar_hotkeys()

        

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
            stats_font.render(f"Dano: {dano:.1f}", True, (243, 236, 215)),
            stats_font.render(f"Rapidez: {rapidez:.1f}", True, (243, 236, 215)),
            stats_font.render(f"Roubo de Vida: {roubo_de_vida:.1f}", True, (243, 236, 215)),
            stats_font.render(f"Chance de Critico: {chance_de_critico:.1f}%", True, (243, 236, 215)),
            stats_font.render(f"Dano Critico: {dano_critico:.1f}", True, (243, 236, 215)),
            stats_font.render(f"Modificador: {modificador}", True, (243, 236, 215))
        ]

        for i, text in enumerate(texts):
            text.set_alpha(self.stats_alpha)
            stats_surface.blit(text, (45, 55 + i * 42))

        self.tela.blit(stats_surface, (970, 750))

    def reset_stats_fade(self):
        self.stats_alpha = 0

    def desenhar_hotkeys(self):
        offset_x, offset_y = screen_shaker.offset
        teclas = ["1", "2", "3", "4"]


        for i, slot in enumerate(self.hotkey_slots):
            color = (0, 200, 0, 200) if self.player.hotkeys[i] != 0 else slot["color"]

            slot_surface = Surface((slot["rect"].width, slot["rect"].height), SRCALPHA)
            slot_surface.fill(color)
            draw.rect(slot_surface, (255, 255, 255, 150), slot_surface.get_rect(), 2)
            self.tela.blit(slot_surface, (slot["rect"].x + offset_x, slot["rect"].y + offset_y))

            tecla_texto = self.hotkey_font.render(teclas[i], True, (243, 236, 215))
            self.tela.blit(tecla_texto, (slot["rect"].x + 45 + offset_x, slot["rect"].y - 20 + offset_y))

            if self.player.hotkeys[i] != 0:
                hab_nome = self.player.hotkeys[i]
                texto = self.hotkey_font.render(hab_nome[:4], True, (243, 236, 215))
                texto_rect = texto.get_rect(center=slot["rect"].center)
                self.tela.blit(texto, (texto_rect.x + offset_x, texto_rect.y + offset_y))