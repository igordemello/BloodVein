from pygame import *
import sys
from pygame.locals import QUIT
import math
from bau import Bau
from itensDic import ConjuntoItens
from mapa import Mapa
from inimigos.orb import Orb
import inimigos.MouthOrbBoss as bossmod
from colisao import Colisao
from loja import Loja
from random import randint, sample, choice
import gerenciador_andar
from screen_shake import screen_shaker
from cutscene import Cutscene
from som import GerenciadorDeMusica
from som import musica
from som import GerenciadorDeSom
from som import som
from loja import Loja
from inimigos.morcegosuicida import MorcegoSuicida
from inimigos.caveiradefogo import CaveiraDeFogo
from inimigos.morcegopadrao import MorcegoPadrao
from inimigos.fantasmagaspar import FantasmaGasp
from inimigos.furação import Furacao
from inimigos.nuvemBoss import NuvemBoss
from armas import LaminaDaNoite, Chigatana, Karambit, EspadaDoTita, MachadoDoInverno, EspadaEstelar, MarteloSolar, Arco, ListaMods
from botao import Botao

init()
fonte = font.SysFont("Arial", 24)


class Sala:
    def __init__(self, caminho_mapa, tela, player, gerenciador_andar, set_minimapa_callback):
        self.tela = tela
        self.gerenciador_andar = gerenciador_andar
        self.mapa = Mapa(caminho_mapa,self.tela,self.tela.get_width(),self.tela.get_height(),self.gerenciador_andar)

        self.lista_mods = ListaMods()
        self.loots = []

        self.player = player
        self.colisao = Colisao(self.mapa, self.player)
        self.colisao.adicionar_entidade(player)
        self.set_minimapa = set_minimapa_callback

        self.porta_liberada = False

        self.ranges_doors = self.mapa.get_rangesdoors()

        self.almaspritesheet = image.load('./assets/Itens/almaSpriteSheet.png').convert_alpha()
        
        self.lojista_img = transform.scale(image.load('./assets/Player/Ikoojista.png').convert_alpha(),(62.5,120))

        self.frames_alma = [self.almaspritesheet.subsurface(Rect(i * 32, 0, 32, 32)) for i in range(4)]

        self.frame_alma_idx = 0
        self.tempo_anterior_alma = time.get_ticks()
        self.duracao_frame_alma = 200
        self.itensDisp = ConjuntoItens()
        self.colliders = self.mapa.get_colliders()

        self.loja = Loja(self.itensDisp,self.player)


        self.em_transicao = False
        self.visitada = False
        self.cutscene = None

        self.spawn_points = self.mapa.get_inimigospawn()  
        self.leve_atual = 0
        self.max_leves = randint(2,5)
        #self.max_leves = 0
        self.inimigos_por_leva = 1 
        self.tempo_entrada = time.get_ticks() 
        self.cooldown_inicial = 1000  
        self.inimigos_spawnados = False
        self.cooldown_entre_levas = 1000  
        self.tempo_ultima_leva = 0  
        self.aguardando_nova_leva = False 

        self.fumaça_particula = [] 
        self.ultima_fumaça = 0
        self.intervalo_fumaça = 100

        tipo = self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo']
        bau_aberto = self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual].get('bau_aberto', False)
        self.bau_interagido = False
        self.ativar_menu_bau = False # eu adicionei isso aqui depois de fazer o iniciar e continuar por conta de um erro que estava dando, se DO NADA der merda no bau a culpa é disso e eu vou me matar
        if tipo == 'bau':
            x, y = self.mapa.get_rangebau()[0].topleft
            self.bau = Bau(self.itensDisp, x, y)
            
            if bau_aberto:
                self.bau.aberto = True
                self.bau.animando = False
                self.bau.frame_index = len(self.bau.frames) - 1
                self.bau.image = self.bau.frames[-1]
                self.bau.menu_ativo = False  # Garante que não reabra
            else:
                self.ativar_menu_bau = False
        else:
            self.bau = None

        if tipo == "boss" and not gerenciador_andar.sala_foi_conquistada(gerenciador_andar.sala_atual):
            fundo = self.tela.copy()
            numerodoandar = self.gerenciador_andar.numero_andar

            if numerodoandar == 1:
                cenas = [
                    {"imagem": transform.scale(image.load("assets/cutscene/player.png").convert_alpha(), (640,960)), "fala": "Por essa eu não esperava, agora tem um gigante ter um gigante desse olho maldito....", "lado": "esquerda"},
                    {"imagem": transform.scale(image.load("assets/cutscene/olhoBoss.png").convert_alpha(), (840,840)), "fala": "Você realmente achou que iria assasinar meus filhos e ficar impune? Você sangra? VAI SANGRAR", "lado": "direita"}
                ]
                self.cutscene = Cutscene(cenas, fundo, self.tela.get_width(), self.tela.get_height())

            if numerodoandar == 2:
                cenas = [
                    {"imagem": transform.scale(image.load("assets/cutscene/nuvemBoss.png").convert_alpha(), (800,800)), "fala": "Matar aquele olho nojento é fácil, quero ver conseguir desviar de algo que está por todo canto!", "lado": "direita"},
                    {"imagem": transform.scale(image.load("assets/cutscene/player.png").convert_alpha(), (640,960)), "fala": "Vai ser ez, eu nunca perderia pra uma nuvem", "lado": "esquerda"}
                    
                ]
                self.cutscene = Cutscene(cenas, fundo, self.tela.get_width(), self.tela.get_height())




        if not gerenciador_andar.sala_foi_conquistada(gerenciador_andar.sala_atual):  
            self.inimigos = self._criar_inimigos()
        else:
            self.inimigos = []
            self.porta_liberada = True
            self.visitada = True

        for inimigo in self.inimigos:
            self.colisao.adicionar_entidade(inimigo)


        self.musicas_de_combate = [
        "BloodVein SCORE/OST/MusicaDeCombate.mp3",
        "BloodVein SCORE/OST/MusicaDeCombate2.mp3"
        ]

        self.musica_escolhida = choice(self.musicas_de_combate)
        self.boss_musica = 0

  
    def _criar_inimigos(self):
        if self.gerenciador_andar.sala_foi_conquistada(self.gerenciador_andar.sala_atual):
            self.leve_atual = self.max_leves + 2
            return []
        tipo_sala = self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]["tipo"]

        if 'spawn' in tipo_sala:
            self.leve_atual = self.max_leves + 2
            return []

        self.leve_atual = self.max_leves + 2
        return []
        
        tempo_atual = time.get_ticks()
        if tempo_atual - self.tempo_entrada < self.cooldown_inicial and not self.inimigos_spawnados:
            return [] 
        
        if "boss" in tipo_sala:
            self.boss_musica = "suicidio"
            musica.tocar("BloodVein SCORE/OST/MusicaDoBoss.mp3")
            xboss,yboss= self.spawn_points[0]
            numero = self.gerenciador_andar.numero_andar
            if numero == 1:
                boss = bossmod.MouthOrb(xboss, yboss)
                boss.nome_base = "Mãe Orbe"
                self.leve_atual = self.max_leves + 2
                return[boss]
            elif numero == 2:
                boss = NuvemBoss(xboss, yboss)
                boss.nome_base = "Nuvem Sombria"
                self.leve_atual = self.max_leves + 2
                return[boss]

        
        
        self.inimigos_spawnados = True

        if not self.visitada:
            self.leve_atual = 0

        if self.leve_atual < self.max_leves:
            self.leve_atual += 1
            inimigos = []
            
            for x, y in self.spawn_points:
                testrect = Rect(x,y,50,50)
                if self.player.get_hitbox().colliderect(testrect):
                    continue
                inimigo = self._criar_inimigo_aleatorio(x, y, tipo_sala)
                inimigos.append(inimigo)
            
            return inimigos
        
        return []

    def _criar_inimigo_aleatorio(self, x, y, tipo_sala):
        elite = "bau" in tipo_sala

        tipos_disponiveis = ["furacao","caveiradefogo","fantasmagaspar","morcegopadrao","morcegosuicida","orb"]
        tipo_escolhido = choice(tipos_disponiveis)


        if tipo_escolhido == "furacao":
            inimigo = Furacao(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Furacão"
            inimigo.aplicar_modificadores(elite=elite)


        elif tipo_escolhido == "caveiradefogo":
            inimigo = CaveiraDeFogo(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Caveira de Fogo"
            inimigo.aplicar_modificadores(elite=elite)

        elif tipo_escolhido == "fantasmagaspar":
            inimigo = FantasmaGasp(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Fantasma Gaspar"
            inimigo.aplicar_modificadores(elite=elite)

        elif tipo_escolhido == "morcegopadrao":
            inimigo = MorcegoPadrao(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Morcego Padrão"
            inimigo.aplicar_modificadores(elite=elite)

        elif tipo_escolhido == "morcegosuicida":
            inimigo = MorcegoSuicida(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Morcego Suicida"
            inimigo.aplicar_modificadores(elite=elite)

        elif tipo_escolhido == "orb":
            inimigo = Orb(x, y, 64, 64, hp=200 if not elite else 300)
            inimigo.nome_base = "Orb"
            inimigo.aplicar_modificadores(elite=elite)

        # Adicione outros tipos de inimigos aqui no futuro:
        # elif tipo_escolhido == "novo_inimigo":
        #     inimigo = NovoInimigo(x, y, ...)

        return inimigo


    def particulas_fumaça(self,x,y):
        return{'x': x + randint(-10,20),
               'y': y + randint(-10,10),
               "size": randint(5,15),
               'alpha': randint(30,100),
               'life': randint(500,1000),
               'created': time.get_ticks(),
               'color': (228, 212, 211)
               }


    def atualizar(self,dt,teclas, eventos):


        if self.cutscene and self.cutscene.ativa:
            self.cutscene.update(eventos)  # ou eventos se estiver usando eventos
            return  # pausa o resto da sala
        
        agora = time.get_ticks()

        temp_rect_player = Rect(self.player.get_hitbox().x, self.player.get_hitbox().y+90, self.player.get_hitbox().width, self.player.get_hitbox().height-90)
        em_espinhos = any(temp_rect_player.colliderect(e) for e in self.mapa.get_espinhos())

        if em_espinhos:
            if not self.player.em_espinhos:
                self.player.em_espinhos = True
                self.player.velocidadeMov = 0.2
                self.player.tomar_dano(10)
                self.player.tempo_ultimo_dano_espinhos = time.get_ticks()
            
            elif time.get_ticks() - self.player.tempo_ultimo_dano_espinhos >= self.player.cooldown_dano_espinhos:
                self.player.tomar_dano(10)
                self.player.tempo_ultimo_dano_espinhos = time.get_ticks()
                

        else:
            if self.player.em_espinhos:
                self.player.em_espinhos = False
                self.player.velocidadeMov = self.player.velocidade_base  

        if not any(inimigo.vivo for inimigo in self.inimigos) and self.leve_atual < self.max_leves:
            if not self.aguardando_nova_leva:
                self.aguardando_nova_leva = True
                self.tempo_ultima_leva = agora
            elif agora - self.tempo_ultima_leva >= self.cooldown_entre_levas:
                self.aguardando_nova_leva = False
                nova_leva = self._criar_inimigos()
                self.inimigos.extend(nova_leva)
            
                for inimigo in nova_leva:
                    self.colisao.adicionar_entidade(inimigo)

        for inimigo in self.inimigos:
            if inimigo.vivo and self.player.hp > 0:
                try:
                    inimigo.atualizar((self.player.x, self.player.y), self.tela, self.inimigos, self.colliders)
                except TypeError:
                    inimigo.atualizar((self.player.x, self.player.y), self.tela)
                inimigo.dar_dano = lambda val=inimigo.dano: self.player.tomar_dano(val)


        self.colisao.checar_colisoes(dt)
        for inimigo in self.inimigos:
            if inimigo not in self.colisao.entidades:
                self.colisao.adicionar_entidade(inimigo)

        if not self.visitada:
            self.porta_liberada = False
            if self.player.x > 50 and self.player.x < self.tela.get_width() - 50:
                self.visitada = True
        else:
            self.porta_liberada = (not any(inimigo.vivo for inimigo in self.inimigos) and self.leve_atual >= self.max_leves and not self.aguardando_nova_leva)

        if self.pode_trocar_de_sala() and teclas[K_e]:
            original_pos = (self.player.x, self.player.y)
            original_vel = (self.player.vx, self.player.vy)

            if self.player.itemAtivo is not None:
                if not self.player.itemAtivo.afetaIni:
                    # Remove efeitos mas mantém a posição/velocidade
                    self.player.itemAtivo.remover_efeitos(self.player)
                    self.player.x, self.player.y = original_pos
                    self.player.vx, self.player.vy = original_vel


            if self.player.itemAtivoEsgotado is not None :
                if not self.player.itemAtivoEsgotado.afetaIni:
                    self.player.itemAtivoEsgotado.remover_efeitos()
                    self.player.x, self.player.y = original_pos
                    self.player.vx, self.player.vy = original_vel
                self.player.itemAtivoEsgotado = None
            self.player.player_rect.topleft = (self.player.x, self.player.y)

            

            self._trocar_de_sala()
            

        if self.porta_liberada and self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'boss' and any(self.player.get_hitbox().colliderect(portal) for portal in self.mapa.get_trocar_andar()) and teclas[K_e]:
            original_pos = (self.player.x, self.player.y)
            original_vel = (self.player.vx, self.player.vy)

            if self.player.itemAtivo is not None:
                if not self.player.itemAtivo.afetaIni:
                    # Remove efeitos mas mantém a posição/velocidade
                    self.player.itemAtivo.remover_efeitos(self.player)
                    self.player.x, self.player.y = original_pos
                    self.player.vx, self.player.vy = original_vel


            if self.player.itemAtivoEsgotado is not None :
                if not self.player.itemAtivoEsgotado.afetaIni:
                    self.player.itemAtivoEsgotado.remover_efeitos()
                    self.player.x, self.player.y = original_pos
                    self.player.vx, self.player.vy = original_vel
                self.player.itemAtivoEsgotado = None
            self.player.player_rect.topleft = (self.player.x, self.player.y)

            self.avancar_andar()


        if self.bau:
            self.bau.update(player_hitbox=self.player.get_hitbox())
            
            if not self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual].get("bau_aberto", False):
                if self.player.get_hitbox().colliderect(self.bau.rect) and teclas[K_e] and self.porta_liberada:
                    if not self.bau.aberto:
                        self.bau.abrir()
                        self.player.vx = 0
                        self.player.vy = 0
                        self.player.travado = True

            
            if (self.bau.aberto and not self.bau.animando and not self.ativar_menu_bau and not self.bau_interagido and self.player.get_hitbox().colliderect(self.bau.rect)):
                self.ativar_menu_bau = True
                self.bau_interagido = True 

            if not self.bau.menu_ativo and self.ativar_menu_bau:
                self.ativar_menu_bau = False
                self.player.travado = False

        now = time.get_ticks()

        if not self.gerenciador_andar.sala_foi_conquistada(self.gerenciador_andar.sala_atual):
            if (not any(inimigo.vivo for inimigo in self.inimigos)) and self.leve_atual < self.max_leves:
                som.tocar("Spawn")
                # entre levas, mostrar fumaça
                if now - int(self.ultima_fumaça) > self.intervalo_fumaça:
                    for x, y in self.spawn_points:
                        self.fumaça_particula.append(self.particulas_fumaça(x, y))
                    self.ultima_fumaça = now

                for particula in self.fumaça_particula[:]:
                    particula['alpha'] -= 0.4
                    particula['size'] += 0.2
                    if now - particula['created'] > particula['life'] or particula['alpha'] <= 0:
                        self.fumaça_particula.remove(particula)
            else:
                self.fumaça_particula.clear()


        if (any((inimigo.vivo for inimigo in self.inimigos)) or self.leve_atual < self.max_leves) and not self.gerenciador_andar.sala_foi_conquistada(self.gerenciador_andar.sala_atual):
            if self.boss_musica == 0:
                musica.tocar(self.musica_escolhida)
        elif self.boss_musica == 0 and self.loja.musica == 0:
            musica.tocar("BloodVein SCORE/OST/MapaForadoCombate.mp3")
            self.musica_escolhida = choice(self.musicas_de_combate)

        for evento in eventos:
            if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                for botao, arma in self.loots[:]:
                    if botao.checkForInput(mouse.get_pos()):
                        arma.aplicaModificador()
                        self.player.inventario.append(arma)
                        self.loots.remove((botao, arma))



    def desenhar_inimigos(self, tela):
        offset_x, offset_y = screen_shaker.offset
        for inimigo in self.inimigos:
            if inimigo.vivo:
                inimigo.desenhar(tela, (self.player.x, self.player.y), offset=(offset_x, offset_y))
            else:
                if not getattr(inimigo, "alma_coletada", True):
                    if not hasattr(inimigo, "vai_dropar_alma"):
                        inimigo.vai_dropar_alma = randint(0, 1) == 1  # decide 50/50 uma vez
                    if inimigo.vai_dropar_alma:
                        pos = (inimigo.x + 16, inimigo.y + 16)
                        self.desenha_alma(pos)
                        alma_hitbox = Rect(0, 0, 50, 50)
                        alma_hitbox.center = pos
                        if self.player.get_hitbox().colliderect(alma_hitbox):
                            self.player.almas += 1
                            inimigo.alma_coletada = True
                if not getattr(inimigo, "loot_coletado", True):
                    if not hasattr(inimigo, "vai_dropar_loot"):
                        inimigo.vai_dropar_loot = randint(1, 100) <= 100  # 30% de chance de cair loot

                    if getattr(inimigo, "vai_dropar_loot", False) and not hasattr(inimigo, "loot_botao_criado"):
                        pos = (inimigo.x + 16, inimigo.y + 32)
                        chance = randint(1, 100)
                        if chance <= 70:
                            raridade = "comum"
                            cor = (255, 255, 255)
                            hover = (100, 100, 100)
                        elif chance <= 90:
                            raridade = "incomum"
                            cor = (0, 255, 0)
                            hover = (0, 100, 0)
                        elif chance <= 97:
                            raridade = "raro"
                            cor = (128, 0, 128)
                            hover = (28, 0, 28)
                        else:
                            raridade = "lendaria"
                            cor = (255, 255, 0)
                            hover = (100, 100, 0)

                        arma_tipo = choice([
                            LaminaDaNoite, Chigatana, Karambit, EspadaDoTita,
                            MachadoDoInverno, EspadaEstelar, MarteloSolar, Arco
                        ])
                        arma = arma_tipo(raridade, self.lista_mods)

                        fontinha = font.Font("assets/fontes/alagard.ttf", 18)
                        texto_render = fontinha.render(arma.nome, True, cor)
                        largura = texto_render.get_width() + 20
                        altura = texto_render.get_height() + 10

                        fundo = Surface((largura, altura), SRCALPHA)
                        fundo.fill((0, 0, 0, 160))  # fundo preto semi-transparente

                        botao = Botao(
                            image=fundo,
                            pos=pos,
                            text_input=arma.nome,
                            font=fontinha,
                            base_color=cor,
                            hovering_color=hover,
                            value=arma
                        )

                        self.loots.append((botao, arma))
                        inimigo.loot_botao_criado = True

    def desenhar(self, tela):

        if self.cutscene and self.cutscene.ativa:
            self.cutscene.draw(self.tela)
            return
        
        offset_x, offset_y = screen_shaker.offset
        self.mapa.desenhar(self.porta_liberada)

        

        if self.bau:
            tela.blit(self.bau.image, (self.bau.rect.x + offset_x, self.bau.rect.y + offset_y))
            

        offset_x, offset_y = screen_shaker.offset

        # Desenhar fumaça nos spawn points
        for particula in self.fumaça_particula:
            s = Surface((particula['size'] * 2, particula['size'] * 2), SRCALPHA)
            draw.circle(
                s, 
                (*particula['color'], particula['alpha']),
                (particula['size'], particula['size']),
                particula['size']
            )
            tela.blit(s, (
                particula['x'] - particula['size'] + offset_x, 
                particula['y'] - particula['size'] + offset_y
            ))
    

        if self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'loja':
            self.tela.blit(self.lojista_img, (950 + offset_x, 650 + offset_y))
        

        #debug visual das colisões do player e do mapa:
        # for collider in self.mapa.get_colliders():
        #     draw.rect(tela, (255,0,0), collider['rect'], 1)
        # draw.rect(tela, (0,255,0), self.player.player_rect, 2)
        for botao, _ in self.loots:
            botao.update(tela)
            botao.changeColor(mouse.get_pos())
        



    def pode_trocar_de_sala(self):

        return self.porta_liberada and any(self.player.get_hitbox().colliderect(rangee['colisor']) for rangee in self.ranges_doors)


    def _trocar_de_sala(self):
        if self.em_transicao:
            return
        self.fade(fade_in=False, duration=2000)
        som.tocar('passar_porta')
        for porta in self.ranges_doors:
            if self.player.get_hitbox().colliderect(porta['colisor']) and self.porta_liberada:
                
                
                self.em_transicao = True



                if not any(inimigo.vivo for inimigo in self.inimigos) and self.leve_atual >= self.max_leves:
                    self.gerenciador_andar.marcar_sala_conquistada(self.gerenciador_andar.sala_atual)

                codigo_porta = porta['codigoporta']

                if codigo_porta in self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual].get("portas", {}):

                    direcao_porta = codigo_porta
                    nova_sala = self.gerenciador_andar.ir_para_proxima_sala(codigo_porta)

                    if nova_sala:
                        nova_instancia = Sala(nova_sala, self.tela, self.player, self.gerenciador_andar, self.set_minimapa)

                        nova_instancia.player = self.player
                        nova_instancia.gerenciador_andar = self.gerenciador_andar
                        
                        if direcao_porta == 'cima':
                            nova_instancia.player.player_rect.topleft = (914, 765)
                        elif direcao_porta == 'baixo':
                            nova_instancia.player.player_rect.topleft = (914, 360)
                        elif direcao_porta == 'esquerda':
                            nova_instancia.player.player_rect.topleft = (1475, 506)
                        elif direcao_porta == 'direita':
                            nova_instancia.player.player_rect.topleft = (350, 506)
                        else:
                            nova_instancia.player.player_rect.topleft = (self.tela.get_width() // 2, self.tela.get_height() // 2)

                        self.__dict__.update(nova_instancia.__dict__)

                        self.player.proibir_dash_ate = time.get_ticks() + 300

                        self.player.resetar_estado_temporario()




                        print(f"Transição para: {nova_sala} via {codigo_porta}")
                self.em_transicao = False
                self.fade(fade_in=True, duration=2000)
                break


    def desenha_alma(self,pos):
        tempo_atual = time.get_ticks()
        if tempo_atual - self.tempo_anterior_alma >= self.duracao_frame_alma:
            self.tempo_anterior_alma = tempo_atual
            self.frame_alma_idx = (self.frame_alma_idx + 1) % len(self.frames_alma)

        frame = self.frames_alma[self.frame_alma_idx]
        frame = transform.scale(frame, (64, 64))
        rect = frame.get_rect(center=pos)
        self.tela.blit(frame, rect)

    def fade(self, fade_in=True, duration=500):
        """Efeito de transição de fade (para entrada ou saída de sala)
        Args:
            fade_in (bool): Se True, fade de preto para tela (entrada). Se False, fade para preto (saída).
            duration (int): Duração total do efeito em milissegundos.
        """
        fade_surface = Surface((1323, 720), SRCALPHA)
        steps = 30
        #delay = max(1, duration // steps)  # Garante pelo menos 1ms de delay

        if fade_in:
            # Fade in (preto -> tela)
            for alpha in range(255, -1, -255 // steps):
                self.desenhar(self.tela)
                fade_surface.fill((0, 0, 0, alpha))
                self.tela.blit(fade_surface, (300, 275))
                display.flip()
                #time.delay(delay)
        else:
            # Fade out (tela -> preto)
            for alpha in range(0, 256, 255 // steps):
                self.desenhar(self.tela)
                fade_surface.fill((0, 0, 0, alpha))
                self.tela.blit(fade_surface, (300, 275))
                display.flip()
                #time.delay(delay)

    def avancar_andar(self):
        # Verifica se é sala do boss e se colidiu com o portal
        portal = self.mapa.get_trocar_andar()
        if (self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]['tipo'] == 'boss' and 
            self.player.get_hitbox().colliderect(portal[0]) and 
            self.porta_liberada):
            
            self.boss_musica = 0

            # Pré-salva o andar atual (opcional)
            andar_num = self.gerenciador_andar.numero_andar
            import shutil
            shutil.copy('data/andar_atual.json', f'data/backup_andar{andar_num}.json')
            
            # Avança para o próximo andar
            self.gerenciador_andar.numero_andar += 1
            self.gerenciador_andar.gerar_andar(self.gerenciador_andar.numero_andar)
            
            # Recria a sala com o novo andar
            spawn_id = self.gerenciador_andar.get_sala_spawn()
            self.gerenciador_andar.sala_atual = spawn_id
            caminho_tmx = self.gerenciador_andar.get_arquivo_atual()

            from minimapa import Minimapa
            self.set_minimapa(Minimapa(self.gerenciador_andar, self.tela))

            nova_sala = Sala(
                caminho_tmx,
                self.tela,
                self.player,
                self.gerenciador_andar,
                self.set_minimapa
            )
            self.__dict__.update(nova_sala.__dict__)

    def get_save_data(self):
        return {
            'porta_liberada': self.porta_liberada,
            'visitada': self.visitada,
            'bau': {
                'aberto': self.bau.aberto if self.bau else False,
                'interagido': self.bau_interagido,
                'menu_ativo': getattr(self, 'ativar_menu_bau', False)
            } if self.bau else None,
            'em_transicao': self.em_transicao
        }

    def load_save_data(self, data, conjunto_itens):

        self.porta_liberada = data['porta_liberada']
        self.visitada = data['visitada']
        self.em_transicao = data.get('em_transicao', False)
        
        
        if data['bau'] and self.bau:
            self.bau.aberto = data['bau']['aberto']
            self.bau_interagido = data['bau']['interagido']
            self.ativar_menu_bau = data['bau']['menu_ativo']
            
            if self.bau.aberto:
                self.bau.animando = False
                self.bau.frame_index = len(self.bau.frames) - 1
                self.bau.image = self.bau.frames[-1]
        
        self.colisao.entidades = [self.player] + self.inimigos

        
    def hitbox_loja(self):
        tipo_sala = self.gerenciador_andar.grafo.nodes[self.gerenciador_andar.sala_atual]["tipo"]
        if not 'loja' in tipo_sala:
            return []
        
        range_loja = self.mapa.get_rangeloja()

        return range_loja if range_loja else []

