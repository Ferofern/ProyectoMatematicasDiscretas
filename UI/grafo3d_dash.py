import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import networkx as nx
import numpy as np
from Data.extraer_datos import extraer_datos

enviados, recibidos = extraer_datos("Data/DatasetRelaciones.xlsx")

G = nx.DiGraph()
for e, r in zip(enviados, recibidos):
    G.add_edge(e, r)

pos = nx.spring_layout(G, dim=3, seed=42)
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]
nodes = list(G.nodes())

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

    # Colores dinámicos usando BFS y degradado
    colores = ['skyblue'] * len(nodes)
    if nodo_seleccionado is not None:
        # BFS para calcular distancias
        distances = nx.single_source_shortest_path_length(G, nodo_seleccionado)
        max_dist = max(distances.values()) if distances else 1
        for i, n in enumerate(nodes):
            if n == nodo_seleccionado:
                colores[i] = 'rgb(255,0,0)'  # nodo seleccionado rojo
            elif n in distances:
                # degradado rojo->naranja->más claro según distancia
                ratio = distances[n] / max_dist
                r = 255
                g = int(165 * ratio)  # naranja = 255,165,0
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

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Grafo 3D Interactivo"),
    dcc.Graph(id='grafo3d', figure=generar_fig()),
])

@app.callback(
    Output('grafo3d', 'figure'),
    Input('grafo3d', 'clickData')
)
def resaltar_vecinos(clickData):
    if clickData is None:
        return generar_fig()
    nodo = clickData['points'][0]['text']
    return generar_fig(nodo_seleccionado=nodo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
