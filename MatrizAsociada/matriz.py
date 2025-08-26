import sys
import numpy as np
import pandas as pd
from Data.extraer_datos import extraer_datos

def construir_matriz_adyacencia(enviados, recibidos):
    nodos = sorted(set(enviados) | set(recibidos))
    n = len(nodos)
    indice = {nodo: i for i, nodo in enumerate(nodos)}
    A = np.zeros((n, n), dtype=int)
    for e, r in zip(enviados, recibidos):
        A[indice[e], indice[r]] = 1
    return A, nodos

def main():
    if len(sys.argv) < 2:
        print("Uso: python matriz.py k")
        sys.exit(1)
    try:
        k = int(sys.argv[1])
    except ValueError:
        print("k debe ser un número entero")
        sys.exit(1)

    enviados, recibidos = extraer_datos('Data/DatasetRelaciones.xlsx')
    A, nodos = construir_matriz_adyacencia(enviados, recibidos)
    
    print("Matriz de adyacencia A:")
    print(pd.DataFrame(A, index=nodos, columns=nodos))

    A_k = np.linalg.matrix_power(A, k)
    print(f"\nMatriz A^{k}:")
    print(pd.DataFrame(A_k, index=nodos, columns=nodos))

if __name__ == "__main__":
    main()
