import json
import networkx as nx
from random import randint,shuffle,choice


class GerenciadorAndar:
    def __init__(self, caminho_json):
        self.gerar_andar(1)

        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.grafo = nx.node_link_graph(data)

        # DESCOMENTAR QUANDO TIVERMOS SALVANDO PROGRESSO, ALÉM DISSO TRAZER O ALGORITIMO QUE GERA O GRAFO DO ANDAR
        #  PRO PROJETO COMO UMA FUNC NESSA CLASSE MESMO, ELE JÁ TA PRONTO, VAI SER EZ DE INTEGRAR AQUI :) :) :) :)
        # ALÉM DE FAZER GERAR INIMIGO DE MANEIRA ALEATÓRIA NA SALA, MAS ISSO AI É UMA TASK DE BOA E QUE DEVE SER FEITA QUANDO TIVERMOS MAIS INIMIGOS ALÉM DA BOLA

        arquivos = [f'{i}.tmx' for i in range(1,15)]
        shuffle(arquivos)
        print(arquivos)

        i=0
        for sala in self.grafo.nodes:
            arquivotmx = arquivos[i]
            self.grafo.nodes[sala]["arquivotmx"] = arquivotmx
            i+=1

        with open(caminho_json, 'w', encoding='utf-8') as f:
            updated_data = nx.node_link_data(self.grafo)
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        self.sala_atual = self.get_sala_spawn()

        self.salas_conquistadas = set()

        self.salas_visitadas = set()
        self.salas_visitadas.add(self.sala_atual) 

    
    def gerar_andar(self, num_andar):
        numsalas = randint(12,14)
        maior_distancia = -1
        sala_inicio = None
        sala_fim = None
        G = nx.Graph()


        direcoes = {
            "cima": (0, -1),
            "baixo": (0, 1),
            "esquerda": (-1, 0),
            "direita": (1, 0)
        }


        oposto = {
            "cima": "baixo",
            "baixo": "cima",
            "esquerda": "direita",
            "direita": "esquerda"
        }


        posicoes = {}  
        ocupado = set() 


        salas = [f"sala{i}" for i in range(numsalas)]
        G.add_nodes_from(salas)

        salas_conectadas = [salas[0]]
        salas_nao_conectadas = salas[1:]

        posicoes[salas[0]] = (0, 0)
        ocupado.add((0, 0))


        while salas_nao_conectadas:
            salas_disponiveis = [s for s in salas_conectadas if G.degree[s] < 3]
            if not salas_disponiveis: break
            
            s1 = choice(salas_disponiveis)
            x1, y1 = posicoes[s1]

            dir_escolhida = None

            for direcao, (dx,dy) in direcoes.items():
                nova_pos = (x1 + dx, y1 + dy)
                if nova_pos not in ocupado:
                    dir_escolhida = direcao
                    break

            if dir_escolhida is None:
                continue

            dx,dy = direcoes[dir_escolhida]
            nova_pos = (x1 + dx, y1 + dy)


            s2 = salas_nao_conectadas.pop(0)
            posicoes[s2] = nova_pos
            ocupado.add(nova_pos)

            G.add_edge(s1, s2)
            salas_conectadas.append(s2)

            if "portas" not in G.nodes[s1]:
                G.nodes[s1]["portas"] = {}
            if "portas" not in G.nodes[s2]:
                G.nodes[s2]["portas"] = {}

            G.nodes[s1]["portas"][dir_escolhida] = s2
            G.nodes[s2]["portas"][oposto[dir_escolhida]] = s1



        um = [n for n in G.nodes if G.degree[n] == 1]

        if not um:
            for sala in G.nodes:
                if G.degree[sala] == 2:
                    vizinhos = list(G.neighbors(sala))
                    if vizinhos:
                        G.remove_edge(sala, vizinhos[0])
                        break

        for sala_a in G.nodes:
            distancias = nx.single_source_shortest_path_length(G, sala_a)
            for sala_b, distancia in distancias.items():
                if distancia > maior_distancia and G.degree(sala_b)==1:
                    maior_distancia = distancia
                    sala_inicio = sala_a
                    sala_fim = sala_b


        G.nodes[sala_inicio]["tipo"] = "spawn"
        G.nodes[sala_fim]["tipo"] = "boss"

        umaporta = []
        duasportas = []
        tresportas = []

        for sala in G.nodes:
            G.nodes[sala]["pos"] = list(posicoes[sala])

            grau = G.degree[sala]
            if grau == 1:
                umaporta.append(sala)
            elif grau == 2:
                duasportas.append(sala)
            elif grau == 3:
                tresportas.append(sala)

            if "tipo" not in G.nodes[sala]:
                G.nodes[sala]["tipo"] = "comum"
                print(f"Setando tipo 'comum' para {sala}")

            G.nodes[sala]["visitada"] = (G.nodes[sala]["tipo"] == "spawn")
            G.nodes[sala]["arquivotmx"] = None
            G.nodes[sala]["salaanterior"] = None

            vizinhos = list(G.neighbors(sala))
            G.nodes[sala]["conexoes"] = vizinhos
            if "portas" not in G.nodes[sala]:
                G.nodes[sala]["portas"] = {}


        with open(f'data/andar{num_andar}.json', 'w', encoding='utf-8') as f:
            json.dump(nx.node_link_data(G), f, ensure_ascii=False, indent=4)



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