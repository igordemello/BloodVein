import json
import networkx as nx
from random import randint,shuffle


class GerenciadorAndar:
    def __init__(self, caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.grafo = nx.node_link_graph(data)

        # DESCOMENTAR QUANDO TIVERMOS SALVANDO PROGRESSO, ALÉM DISSO TRAZER O ALGORITIMO QUE GERA O GRAFO DO ANDAR
        #  PRO PROJETO COMO UMA FUNC NESSA CLASSE MESMO, ELE JÁ TA PRONTO, VAI SER EZ DE INTEGRAR AQUI :) :) :) :)
        # ALÉM DE FAZER GERAR INIMIGO DE MANEIRA ALEATÓRIA NA SALA, MAS ISSO AI É UMA TASK DE BOA E QUE DEVE SER FEITA QUANDO TIVERMOS MAIS INIMIGOS ALÉM DA BOLA

        # arquivos = [f'{i}.tmx' for i in range(1,15)]
        # shuffle(arquivos)
        # print(arquivos)

        # i=0
        # for sala in self.grafo.nodes:
        #     arquivotmx = arquivos[i]
        #     self.grafo.nodes[sala]["arquivotmx"] = arquivotmx
        #     i+=1

        # with open(caminho_json, 'w', encoding='utf-8') as f:
        #     updated_data = nx.node_link_data(self.grafo)
        #     json.dump(updated_data, f, ensure_ascii=False, indent=4)

        self.sala_atual = self.get_sala_spawn()

        self.salas_conquistadas = set()

        self.salas_visitadas = set()
        self.salas_visitadas.add(self.sala_atual) 

    
    # def gerar_grafo():
    #     pass

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
    
    def get_portas_sala(self, sala):
        return self.grafo.nodes[sala].get("portas", {})

    
    def ir_para_proxima_sala(self, codigo_porta):
        porta_direcao = codigo_porta
        
        if porta_direcao in self.grafo.nodes[self.sala_atual].get("portas", {}):
            proxima_sala = self.grafo.nodes[self.sala_atual]["portas"][porta_direcao]
            self.sala_atual = proxima_sala
            self.salas_visitadas.add(proxima_sala)
            return self.grafo.nodes[proxima_sala]["arquivotmx"]
        
    def get_mapa_info(self):
        nodes = []
        
        
        for sala in self.grafo.nodes:
            node_data = self.grafo.nodes[sala]
            nodes.append({
                'id': sala,
                'tipo': node_data['tipo'],
                'visitada': sala in self.salas_visitadas,
                'atual': sala == self.sala_atual,
                'posicao': (
                    (node_data['pos'][0]) * 120 + 350,
                    (node_data['pos'][1]) * 80 + 350
                )
            })
        
        edges = []
        for origem, destino in self.grafo.edges:
            edges.append({
                'origem': origem,
                'destino': destino
            })
            
        
        return {
            'nodes': nodes,
            'edges': edges
        }