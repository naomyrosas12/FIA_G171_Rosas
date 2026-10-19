"""S2 · Problemas de búsqueda y espacios de búsqueda (2.1 y 2.2)

Modela 2 problemas reales como problemas de búsqueda (estado, acciones, costo, meta),
genera el espacio de estados como grafo dirigido y ponderado con NetworkX, dibuja el
diagrama y calcula métricas de complejidad.

  Problema 1: Robot de almacén (papelería/bodega) en una cuadrícula con obstáculos
              y zonas de tráfico lento.
  Problema 2: Repartidor que visita 4 clientes desde un depósito y regresa (tipo TSP,
              el mismo tipo de problema del caso UPS ORION de la S1).

Ejecutar: python s2_problemas_busqueda.py
Requiere: pip install networkx matplotlib
Genera:   figuras/grafo_almacen.png, figuras/grafo_reparto.png y figuras/crecimiento_estados.png
"""
import itertools
import math
import os
from collections import deque

import matplotlib
matplotlib.use("Agg")  # genera PNG sin abrir ventana
import matplotlib.pyplot as plt
import networkx as nx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(AQUI, "figuras")
os.makedirs(FIG, exist_ok=True)


# ======================================================================
# 1. Formulación general de un problema de búsqueda
# ======================================================================
class ProblemaBusqueda:
    """Un problema se define con: estado inicial, acciones, modelo de transición,
    costo de paso y prueba de meta (Russell & Norvig, cap. 3)."""
    nombre = "Problema"

    def estado_inicial(self):
        raise NotImplementedError

    def acciones(self, estado):
        """Lista de acciones aplicables en 'estado'."""
        raise NotImplementedError

    def resultado(self, estado, accion):
        """Estado que resulta de aplicar 'accion' en 'estado'."""
        raise NotImplementedError

    def costo(self, estado, accion, nuevo):
        """Costo de paso (por defecto 1)."""
        return 1

    def es_meta(self, estado):
        raise NotImplementedError


# ======================================================================
# 2. Generador de estados + grafo (sirve para cualquier problema)
# ======================================================================
def generar_grafo(problema):
    """Explora todo el espacio alcanzable (recorrido en anchura) y lo guarda en un
    grafo dirigido: nodo = estado, arista = acción, peso = costo de paso."""
    G = nx.DiGraph()
    inicio = problema.estado_inicial()
    G.add_node(inicio)
    cola = deque([inicio])
    while cola:
        s = cola.popleft()
        for a in problema.acciones(s):
            n = problema.resultado(s, a)
            if n not in G:          # estado nuevo -> se agrega y se explorará
                G.add_node(n)
                cola.append(n)
            G.add_edge(s, n, weight=problema.costo(s, a, n), accion=a)
    return G


# ======================================================================
# 3. Problema 1: robot de almacén en cuadrícula
# ======================================================================
class RobotAlmacen(ProblemaBusqueda):
    """Estado: (fila, columna). Acciones: Arriba, Abajo, Izquierda, Derecha.
    Costo: 1 por celda normal, 3 por celda 'T' (tráfico lento / pasillo ocupado).
    Meta: llegar a 'M'. '#' = estante (obstáculo)."""
    nombre = "Robot de almacén"
    MAPA = [
        "S..#.",
        ".#.T.",
        ".T...",
        ".#.#.",
        "....M",
    ]
    MOV = {"Arriba": (-1, 0), "Abajo": (1, 0), "Izquierda": (0, -1), "Derecha": (0, 1)}

    def __init__(self):
        self.filas, self.cols = len(self.MAPA), len(self.MAPA[0])
        for r, fila in enumerate(self.MAPA):
            for c, ch in enumerate(fila):
                if ch == "S":
                    self.inicio = (r, c)
                elif ch == "M":
                    self.meta = (r, c)

    def estado_inicial(self):
        return self.inicio

    def acciones(self, estado):
        r, c = estado
        libres = []
        for nombre, (dr, dc) in self.MOV.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.filas and 0 <= nc < self.cols and self.MAPA[nr][nc] != "#":
                libres.append(nombre)
        return libres

    def resultado(self, estado, accion):
        dr, dc = self.MOV[accion]
        return (estado[0] + dr, estado[1] + dc)

    def costo(self, estado, accion, nuevo):
        return 3 if self.MAPA[nuevo[0]][nuevo[1]] == "T" else 1

    def es_meta(self, estado):
        return estado == self.meta


# ======================================================================
# 4. Problema 2: repartidor con 4 clientes (tipo TSP)
# ======================================================================
class RepartoClientes(ProblemaBusqueda):
    """Estado: (ubicación, clientes_visitados). Acción: ir a un cliente aún no visitado;
    cuando ya se visitaron todos, volver al depósito. Costo: distancia en km.
    Meta: estar en el depósito con todos los clientes visitados.
    (Distancias de ejemplo; se pueden cambiar por las reales.)"""
    nombre = "Reparto con 4 clientes"
    DEPOSITO = "Depósito"
    CLIENTES = ["A", "B", "C", "D"]
    DIST = {  # km, simétricas
        ("Depósito", "A"): 4, ("Depósito", "B"): 7, ("Depósito", "C"): 6, ("Depósito", "D"): 9,
        ("A", "B"): 3, ("A", "C"): 5, ("A", "D"): 8,
        ("B", "C"): 4, ("B", "D"): 5,
        ("C", "D"): 3,
    }

    def d(self, x, y):
        return self.DIST.get((x, y)) or self.DIST[(y, x)]

    def estado_inicial(self):
        return (self.DEPOSITO, frozenset([self.DEPOSITO]))

    def todos(self):
        return frozenset([self.DEPOSITO] + self.CLIENTES)

    def acciones(self, estado):
        ubic, vis = estado
        pendientes = [c for c in self.CLIENTES if c not in vis]
        if pendientes:
            return pendientes                     # ir al cliente X
        return [self.DEPOSITO] if ubic != self.DEPOSITO else []   # volver

    def resultado(self, estado, accion):
        return (accion, estado[1] | {accion})

    def costo(self, estado, accion, nuevo):
        return self.d(estado[0], accion)

    def es_meta(self, estado):
        return estado[0] == self.DEPOSITO and estado[1] == self.todos()


# ======================================================================
# 5. Análisis: solución óptima y métricas de complejidad
# ======================================================================
def analizar(problema, G):
    inicio = problema.estado_inicial()
    metas = [n for n in G if problema.es_meta(n)]
    camino = nx.dijkstra_path(G, inicio, metas[0], weight="weight")
    costo = nx.dijkstra_path_length(G, inicio, metas[0], weight="weight")
    # profundidad de la solución (nº de acciones) = camino más corto en pasos
    d = nx.shortest_path_length(G, inicio, metas[0])
    V, E = G.number_of_nodes(), G.number_of_edges()
    b = E / V                                   # factor de ramificación promedio
    bmax = max(dict(G.out_degree()).values())   # ramificación máxima (para la cota O(b^d))
    return {"camino": camino, "costo": costo, "d": d, "V": V, "E": E, "b": b, "bmax": bmax, "metas": metas}


def imprimir_resumen(problema, r):
    print(f"\n=== {problema.nombre} ===")
    print(f"Estados (nodos)        : {r['V']}")
    print(f"Transiciones (aristas) : {r['E']}")
    print(f"Factor de ramificación : promedio ≈ {r['b']:.2f}, máximo b = {r['bmax']}")
    print(f"Profundidad solución   : d = {r['d']} acciones")
    print(f"Costo óptimo (Dijkstra): {r['costo']}")
    print(f"Cota en árbol (sin detectar repetidos): O(b^d) = {r['bmax']}^{r['d']} = {r['bmax'] ** r['d']:,} nodos")
    print(f"Búsqueda en grafo (con conjunto de visitados): O(V + E) = {r['V'] + r['E']} pasos")


# ======================================================================
# 6. Dibujo del grafo
# ======================================================================
def dibujar(problema, G, pos, r, etiquetas, archivo, titulo, mostrar_pesos=None, tam=1100):
    fig, ax = plt.subplots(figsize=(11, 7))
    inicio = problema.estado_inicial()
    colores = []
    for n in G:
        if n == inicio:
            colores.append("#2E9E5B")        # inicio
        elif n in r["metas"]:
            colores.append("#D64545")        # meta
        elif n in r["camino"]:
            colores.append("#F2B134")        # en la solución
        else:
            colores.append("#9DB7E8")
    ruta = list(zip(r["camino"][:-1], r["camino"][1:]))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#B8BCC8", arrows=True, arrowsize=10,
                           node_size=tam, connectionstyle="arc3,rad=0.08", width=1)
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=ruta, edge_color="#E07B00", width=3,
                           arrows=True, arrowsize=16, node_size=tam, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores, node_size=tam, edgecolors="#33384A")
    nx.draw_networkx_labels(G, pos, labels=etiquetas, ax=ax, font_size=8)
    if mostrar_pesos:
        nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=mostrar_pesos, font_size=8,
                                     font_color="#B00020", label_pos=0.3)
    ax.set_title(f"{titulo}\n{r['V']} estados · {r['E']} transiciones · costo óptimo = {r['costo']}",
                 fontsize=12, fontweight="bold")
    ax.text(0.01, 0.01, "Verde = inicio · Rojo = meta · Amarillo/naranja = solución óptima",
            transform=ax.transAxes, fontsize=8, color="#555")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, archivo), dpi=150)
    plt.close(fig)


def verificar_por_fuerza_bruta(p):
    """Prueba las n! rutas posibles del reparto y devuelve [(costo, ruta), ...] ordenada.
    Sirve para comprobar que Dijkstra sobre el grafo encontró realmente el óptimo."""
    rutas = []
    for perm in itertools.permutations(p.CLIENTES):
        ruta = [p.DEPOSITO, *perm, p.DEPOSITO]
        costo = sum(p.d(a, b) for a, b in zip(ruta, ruta[1:]))
        rutas.append((costo, ruta))
    return sorted(rutas)


def grafica_crecimiento():
    """Compara cuántas rutas hay (n!) con cuántos estados distintos tiene el grafo."""
    ns = list(range(2, 16))
    estados = [2 + n * 2 ** (n - 1) for n in ns]
    rutas = [math.factorial(n) for n in ns]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.semilogy(ns, rutas, "o-", color="#E8871E", label="Rutas posibles  n!")
    ax.semilogy(ns, estados, "s-", color="#0E4D64", label="Estados del grafo  2 + n·2^(n-1)")
    ax.set_xlabel("Número de clientes (n)")
    ax.set_ylabel("Cantidad (escala logarítmica)")
    ax.set_title("Crecimiento del espacio de búsqueda en el problema de reparto", fontsize=11, fontweight="bold")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "crecimiento_estados.png"), dpi=150)
    plt.close(fig)


def main():
    # ---------- Problema 1: robot de almacén ----------
    p1 = RobotAlmacen()
    G1 = generar_grafo(p1)
    r1 = analizar(p1, G1)
    imprimir_resumen(p1, r1)
    print("Ruta óptima:", " -> ".join(str(e) for e in r1["camino"]))
    pos1 = {(f, c): (c, -f) for (f, c) in G1}                       # posición = celda del mapa
    et1 = {n: f"{n[0]},{n[1]}" for n in G1}
    pesos1 = {(u, v): w["weight"] for u, v, w in G1.edges(data=True) if w["weight"] > 1}
    dibujar(p1, G1, pos1, r1, et1, "grafo_almacen.png",
            "Problema 1 · Robot de almacén (rojo = costo 3 por zona de tráfico)", pesos1)

    # ---------- Problema 2: reparto con 4 clientes ----------
    p2 = RepartoClientes()
    G2 = generar_grafo(p2)
    r2 = analizar(p2, G2)
    imprimir_resumen(p2, r2)
    print("Ruta óptima:", " -> ".join(n[0] for n in r2["camino"]))
    for n in G2:   # capa = cuántos puntos se han visitado (para ordenar el dibujo)
        G2.nodes[n]["capa"] = len(n[1]) + (1 if n[0] == p2.DEPOSITO and len(n[1]) > 1 else 0)
    pos2 = nx.multipartite_layout(G2, subset_key="capa", align="vertical")
    et2 = {n: ("Dep" if n[0] == p2.DEPOSITO else n[0]) for n in G2}
    dibujar(p2, G2, pos2, r2, et2, "grafo_reparto.png",
            "Problema 2 · Reparto con 4 clientes (nodo = ubicación + clientes visitados)", tam=700)

    # ---------- Verificación por fuerza bruta ----------
    todas = verificar_por_fuerza_bruta(p2)
    print(f"Fuerza bruta ({len(todas)} rutas): mejor costo = {todas[0][0]} -> "
          f"coincide con Dijkstra: {todas[0][0] == r2['costo']}")

    # ---------- Complejidad teórica del problema 2 ----------
    n = len(p2.CLIENTES)
    print(f"\nReparto con n={n} clientes: estados = 2 + n·2^(n-1) = {2 + n * 2 ** (n - 1)}; "
          f"rutas posibles = n! = {math.factorial(n)}")
    grafica_crecimiento()
    print("Con n=10 clientes: n! = 3,628,800 rutas (explosión combinatoria) -> se requieren heurísticas (S3).")


if __name__ == "__main__":
    main()