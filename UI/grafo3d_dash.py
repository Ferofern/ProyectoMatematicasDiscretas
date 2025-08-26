import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import networkx as nx
import numpy as np
from Data.extraer_datos import extraer_datos

# Cargar datos
enviados, recibidos = extraer_datos("Data/DatasetRelaciones.xlsx")

# Crear grafo dirigido
G = nx.DiGraph()
for e, r in zip(enviados, recibidos):
    G.add_edge(e, r)

# Posiciones en 3D
pos = nx.spring_layout(G, dim=3, seed=42)
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]
nodes = list(G.nodes())

# Función para generar figura
def generar_fig(nodo_seleccionado=None):
    edge_traces = []
    arrow_size = 0.05
    for edge in G.edges():
        start = np.array(pos[edge[0]])
        end = np.array(pos[edge[1]])
        edge_traces.append(go.Scatter3d(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            z=[start[2], end[2]],
            mode='lines',
            line=dict(color='gray', width=3),
            hoverinfo='none'
        ))

    # Colores dinámicos BFS con degradado
    colores = ['skyblue'] * len(nodes)
    if nodo_seleccionado is not None:
        distances = nx.single_source_shortest_path_length(G, nodo_seleccionado)
        max_dist = max(distances.values()) if distances else 1
        for i, n in enumerate(nodes):
            if n == nodo_seleccionado:
                colores[i] = 'rgb(255,0,0)'  # Nodo seleccionado rojo
            elif n in distances:
                ratio = distances[n] / max_dist
                r = 255
                g = int(165 * ratio)
                b = 0
                colores[i] = f'rgb({r},{g},{b})'

    node_trace = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers+text',
        text=[str(n) for n in nodes],
        textposition="top center",
        marker=dict(size=8, color=colores, line=dict(width=1, color='black')),
        hoverinfo="text",
        hovertext=[f"Nodo: {n}" for n in nodes]
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Grafo Dirigido 3D Interactivo",
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False)
        )
    )
    return fig

# Crear app Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Grafo 3D Interactivo"),
    dcc.Graph(id='grafo3d', figure=generar_fig()),
    html.Div(id="info-nodo", style={"marginTop": "20px", "fontSize": "18px"})
])

# Callback para actualizar grafo + info
@app.callback(
    [Output('grafo3d', 'figure'),
     Output('info-nodo', 'children')],
    Input('grafo3d', 'clickData')
)
def actualizar(clickData):
    if clickData is None:
        return generar_fig(), "Haz clic en un nodo para ver su información."

    nodo = clickData['points'][0]['text']
    fig = generar_fig(nodo_seleccionado=nodo)

    # Información extra
    out_degree = G.out_degree(nodo)  # Número de aristas que salen
    caminos = nx.single_source_shortest_path_length(G, nodo)
    grado_camino = max(caminos.values()) if caminos else 0

    info = (
        f"Nodo seleccionado: {nodo} | "
        f"Nodos de salida: {out_degree} | "
        f"Grado del camino alcanzable: {grado_camino}"
    )

    return fig, info

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
