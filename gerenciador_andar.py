import json
import networkx as nx
from random import randint


class GerenciadorAndar:
    def __init__(self, caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.grafo = nx.node_link_graph(data)

        # DESCOMENTAR QUANDO TIVERMOS SALVANDO PROGRESSO, ALÉM DISSO TRAZER O ALGORITIMO QUE GERA O GRAFO DO ANDAR
        #  PRO PROJETO COMO UMA FUNC NESSA CLASSE MESMO, ELE JÁ TA PRONTO, VAI SER EZ DE INTEGRAR AQUI :) :) :) :)
        # ALÉM DE FAZER GERAR INIMIGO DE MANEIRA ALEATÓRIA NA SALA, MAS ISSO AI É UMA TASK DE BOA E QUE DEVE SER FEITA QUANDO TIVERMOS MAIS INIMIGOS ALÉM DA BOLA
        # for sala in self.grafo.nodes:
        #     grau = self.grafo.degree[sala]
        #     arquivo = f"mapas/{grau}-{randint(1, 5)}.tmx"
        #     self.grafo.nodes[sala]["arquivotmx"] = arquivo

        # with open(caminho_json, 'w', encoding='utf-8') as f:
        #     updated_data = nx.node_link_data(self.grafo)
        #     json.dump(updated_data, f, ensure_ascii=False, indent=4)

        self.sala_atual = self.get_sala_spawn()

        self.salas_conquistadas = set()
        

    def marcar_sala_conquistada(self, sala_id):
        self.salas_conquistadas.add(sala_id)

    def sala_foi_conquistada(self, sala_id):
        return sala_id in self.salas_conquistadas

    def get_sala_spawn(self):
        for sala in self.grafo.nodes:
            if self.grafo.nodes[sala]["tipo"] == "spawn":
                return sala
            
    def get_arquivo_atual(self):
        return self.grafo.nodes[self.sala_atual]["arquivotmx"]
    
    def ir_para_proxima_sala(self, codigo_porta):
        """codigo_porta deve ser no formato 'cdX' onde X é o número"""
        try:
            porta_num = int(codigo_porta.replace("cd", ""))  # Extrai o número da porta
            porta_key = f"p{porta_num}"  # Converte para formato p0, p1, etc.
            
            if porta_key in self.grafo.nodes[self.sala_atual]:
                proxima_sala = self.grafo.nodes[self.sala_atual][porta_key]
                self.sala_atual = proxima_sala
                return self.grafo.nodes[proxima_sala]["arquivotmx"]
        except (ValueError, AttributeError):
            pass
        return None