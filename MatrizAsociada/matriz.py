# MatrizAsociada/matriz.py
import numpy as np
import networkx as nx
from Data.extraer_datos import extraer_datos

def generar_matriz():
    enviados, recibidos = extraer_datos("Data/DatasetRelaciones.xlsx")
    G = nx.DiGraph()
    for e, r in zip(enviados, recibidos):
        G.add_edge(e, r)
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes)
    return A, nodes
