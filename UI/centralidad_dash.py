import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
from Data.extraer_datos import extraer_datos

# ======== Cargar datos desde Excel =========
ruta_excel = "Data/DatasetRelaciones.xlsx"
enviados, recibidos = extraer_datos(ruta_excel)

# Crear grafo dirigido
G = nx.DiGraph()
edges = list(zip(enviados, recibidos))
G.add_edges_from(edges)

# Calcular centralidad de vector propio
centralidad = nx.eigenvector_centrality_numpy(G)

# Multiplicar centralidad por factor para apreciar decimales
f = 1000000000000
centralidad = {k: v*f for k, v in centralidad.items()}

nx.set_node_attributes(G, centralidad, "centralidad")

# Layout 3D
pos = nx.spring_layout(G, dim=3, seed=42)

# ======== Construir Dash =========
app = dash.Dash(__name__)
server = app.server

def crear_figura(top_k=5):
    # Escalar centralidades para tamaño/color
    max_c = max(centralidad.values())
    min_c = min(centralidad.values())
    rango = max_c - min_c if max_c != min_c else 1

    def escalar(valor):
        return 20 + 40 * (valor - min_c) / rango

    # Nodos
    x, y, z, text, sizes, colors = [], [], [], [], [], []
    for node, (x0, y0, z0) in pos.items():
        x.append(x0)
        y.append(y0)
        z.append(z0)
        text.append(f"{node}<br>Centralidad: {centralidad[node]:.4f}")
        sizes.append(escalar(centralidad[node]))
        colors.append(centralidad[node])

    node_trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers+text",
        marker=dict(size=sizes, color=colors, colorscale="YlOrRd", showscale=True),
        text=[n for n in G.nodes()],
        hovertext=text,
        hoverinfo="text"
    )

    # Aristas
    edge_x, edge_y, edge_z, edge_colors = [], [], [], []
    for src, dst in G.edges():
        x0, y0, z0 = pos[src]
        x1, y1, z1 = pos[dst]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

        # Color de la arista promedio de los nodos
        c = (centralidad[src] + centralidad[dst]) / 2
        edge_colors.append(c)

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode="lines",
        line=dict(color="gray", width=2),
        hoverinfo="none"
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, visible=False),
            yaxis=dict(showbackground=False, showticklabels=False, visible=False),
            zaxis=dict(showbackground=False, showticklabels=False, visible=False),
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

# DataFrame de ranking
ranking_df = pd.DataFrame({
    "Nodo": list(centralidad.keys()),
    "Centralidad": list(centralidad.values())
}).sort_values("Centralidad", ascending=False).reset_index(drop=True)
ranking_df.index += 1

# ======== Layout Dash =========
app.layout = html.Div([
    html.H1("Centralidad de Eigenvector", style={"textAlign": "center"}),

    html.Div([
        html.Label("Top k nodos por centralidad:"),
        dcc.Input(id="input-topk", type="number", value=5, min=1, step=1),
        html.Button("Actualizar", id="btn-update", n_clicks=0)
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="grafo-3d", figure=crear_figura()),

    html.H2("Ranking de Centralidad (Eigenvector)", style={"marginTop": "30px"}),

    dash_table.DataTable(
        id="tabla-centralidad",
        columns=[{"name": "#", "id": "#"},
                 {"name": "Nodo", "id": "Nodo"},
                 {"name": "Centralidad", "id": "Centralidad"}],
        data=[{"#": i, "Nodo": row["Nodo"], "Centralidad": f"{row['Centralidad']:.4f}"}
              for i, row in ranking_df.iterrows()],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "5px"},
        style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"}
    )
])

@app.callback(
    Output("grafo-3d", "figure"),
    Output("tabla-centralidad", "data"),
    Input("btn-update", "n_clicks"),
    State("input-topk", "value")
)
def actualizar_vista(n_clicks, topk):
    fig = crear_figura(topk)
    top_df = ranking_df.head(topk)
    data = [{"#": i, "Nodo": row["Nodo"], "Centralidad": f"{row['Centralidad']:.4f}"}
            for i, row in top_df.iterrows()]
    return fig, data

if __name__ == "__main__":
    app.run(debug=True, port=8082)
