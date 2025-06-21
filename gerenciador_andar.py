import json
import networkx as nx
from random import randint


class GerenciadorAndar:
    def __init__(self, caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.grafo = nx.node_link_graph(data)

        # for sala in self.grafo.nodes:
        #     grau = self.grafo.degree[sala]
        #     arquivo = f"mapas/{grau}-{randint(1, 5)}.tmx"
        #     self.grafo.nodes[sala]["arquivotmx"] = arquivo

        # with open(caminho_json, 'w', encoding='utf-8') as f:
        #     updated_data = nx.node_link_data(self.grafo)
        #     json.dump(updated_data, f, ensure_ascii=False, indent=4)

        self.sala_atual = self.get_sala_spawn()

    def get_sala_spawn(self):
        for sala in self.grafo.nodes:
            if self.grafo.nodes[sala]["tipo"] == "spawn":
                return sala
            
    def get_arquivo_atual(self):
        return self.grafo.nodes[self.sala_atual]["arquivotmx"]
    
    def ir_para_proxima_sala(self, codigo_porta):
        print(codigo_porta)
        porta_idx = int(codigo_porta.replace("cd", ""))
        porta_key = f"p{porta_idx}"

        if porta_key in self.grafo.nodes[self.sala_atual]:
            proxima_sala = self.grafo.nodes[self.sala_atual][porta_key]
            self.sala_atual = proxima_sala
            return self.grafo.nodes[proxima_sala]["arquivotmx"]
        return None