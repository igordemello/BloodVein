import heapq

def a_star(matriz, inicio, fim):
    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    largura = len(matriz[0])
    altura = len(matriz)

    if not (0 <= inicio[0] < largura and 0 <= inicio[1] < altura):
        return []
    if not (0 <= fim[0] < largura and 0 <= fim[1] < altura):
        return []
    if matriz[inicio[1]][inicio[0]] != 0 or matriz[fim[1]][fim[0]] != 0:
        return []

    fila = []
    heapq.heappush(fila, (0 + heuristica(inicio, fim), 0, inicio, []))
    visitado = set()

    while fila:
        _, custo, atual, caminho = heapq.heappop(fila)

        if atual in visitado:
            continue
        visitado.add(atual)

        caminho = caminho + [atual]

        if atual == fim:
            return caminho

        x, y = atual
        vizinhos = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for nx, ny in vizinhos:
            if 0 <= nx < largura and 0 <= ny < altura:
                if matriz[ny][nx] == 0:
                    heapq.heappush(fila, (
                        custo + 1 + heuristica((nx, ny), fim),
                        custo + 1,
                        (nx, ny),
                        caminho
                    ))

    return []
