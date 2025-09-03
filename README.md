
# Proyecto Matemáticas Discretas - Visualización de Grafos y Matrices

Este proyecto permite **visualizar grafos dirigidos en 3D** y explorar **matrices de adyacencia y caminos posibles** utilizando Python, Dash, Plotly y NetworkX.

---

## 🔹 Contenido del proyecto

### 1. `UI/grafo3d_dash.py`
- Muestra un grafo 3D interactivo.
- Funcionalidades principales:
  - Seleccionar un nodo haciendo clic (el nodo se pinta de rojo).
  - Visualizar los nodos vecinos con un degradado de colores según la distancia desde el nodo seleccionado.
  - Mostrar el número de aristas de salida del nodo.
  - Indicar el grado máximo de los caminos alcanzables desde el nodo seleccionado.

### 2. `UI/dash_app.py`
- Muestra la **matriz de adyacencia** \(A\) del grafo.
- Permite calcular y visualizar **A^k**, indicando la existencia de caminos de longitud \(k\).
- Visualización mediante Heatmaps interactivos usando Plotly.

### 3. `Data/DatasetRelaciones.xlsx`
- Contiene los nodos y las relaciones para construir el grafo.

### 4. `Data/extraer_datos.py`
- Función para cargar los datos desde el archivo Excel.

---

## ⚙️ Requisitos

- Python 3.8 o superior.
- Administrador de paquetes `pip`.

Instalación de dependencias:

```bash
pip install dash plotly networkx numpy pandas openpyxl
```

O mediante el archivo de requerimientos:

```bash
pip install -r requirements.txt
```

### Ejecución

Ejecutar los tres módulos en paralelo:

```bash
./run.sh
```

**Liberar puertos al finalizar:**

```bash
./cerrar_puertos.sh
```

---

## 🗂️ Estructura del proyecto

```
ProyectoMatematicasDiscretas/
│── Data/
│   ├── DatasetRelaciones.xlsx
│   └── extraer_datos.py
│
│── UI/
│   ├── dash_app.py
│   └── grafo3d_dash.py
│
│── requirements.txt
│── README.md
-Bash
```

---

## 🔹 Tutorial de uso

### Grafo 3D (`grafo3d_dash.py`)
1. Haz clic en un nodo para seleccionarlo (se pintará de rojo).
2. Los nodos alcanzables se pintan con un degradado de rojo a naranja según su distancia.
3. Se muestra el número de aristas de salida del nodo seleccionado.
4. Se muestra el grado máximo de los caminos alcanzables desde ese nodo.

### Matriz de adyacencia (`dash_app.py`)
1. Ingresa un valor de \(k\) en el campo "Potencia k".
2. Se muestran dos Heatmaps:
   - La matriz de adyacencia \(A\).
   - La matriz \(A^k\), indicando la existencia de caminos de longitud \(k\).