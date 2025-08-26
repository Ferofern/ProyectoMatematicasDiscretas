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
nodes = list(G.nodes())
x_nodes = [pos[n][0] for n in nodes]
y_nodes = [pos[n][1] for n in nodes]
z_nodes = [pos[n][2] for n in nodes]

try:
    centrality = nx.eigenvector_centrality_numpy(G)
except Exception:
    centrality = nx.eigenvector_centrality_numpy(G.to_undirected())

cent_vals = np.array([centrality.get(n, 0.0) for n in nodes])
if cent_vals.max() > 0:
    cent_norm = (cent_vals - cent_vals.min()) / (cent_vals.max() - cent_vals.min())
else:
    cent_norm = cent_vals

min_size, max_size = 6, 28
node_sizes = min_size + (max_size - min_size) * cent_norm

def color_from_norm(v):
    # map 0..1 to color from lightyellow -> orange -> red
    r = np.clip(255, 0, 255)
    g = int(200 - 180 * v)
    b = int(50 - 40 * v)
    return f"rgb({r},{g},{b})"

node_colors = [color_from_norm(v) for v in cent_norm]

def build_figure(highlight_top_k=0, selected_node=None):
    edge_traces = []
    arrow_size = 0.05
    for u, v in G.edges():
        start = np.array(pos[u])
        end = np.array(pos[v])
        edge_traces.append(go.Scatter3d(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            z=[start[2], end[2]],
            mode='lines',
            line=dict(color='lightgray', width=2),
            hoverinfo='none'
        ))
        vec = end - start
        vec_len = np.linalg.norm(vec)
        if vec_len == 0:
            continue
        vec_dir = vec / vec_len
        perp1 = np.cross(vec_dir, np.array([0, 0, 1.0]))
        if np.linalg.norm(perp1) < 1e-6:
            perp1 = np.cross(vec_dir, np.array([0, 1.0, 0]))
        perp1 = perp1 / np.linalg.norm(perp1)
        tip1 = end - vec_dir * arrow_size + 0.5 * arrow_size * perp1
        tip2 = end - vec_dir * arrow_size - 0.5 * arrow_size * perp1
        edge_traces.append(go.Mesh3d(
            x=[end[0], tip1[0], tip2[0]],
            y=[end[1], tip1[1], tip2[1]],
            z=[end[2], tip1[2], tip2[2]],
            color='lightgray',
            opacity=0.9,
            hoverinfo='none'
        ))

    colors = node_colors.copy()
    sizes = list(node_sizes)

    if highlight_top_k and highlight_top_k > 0:
        idx_sorted = np.argsort(-cent_vals)
        top_idx = set(idx_sorted[:highlight_top_k].tolist())
        for i in range(len(nodes)):
            if i in top_idx:
                colors[i] = 'rgb(255,0,0)'
                sizes[i] = max_size
            else:
                colors[i] = 'lightgray'
                sizes[i] = min_size

    if selected_node is not None:
        # emphasize selected and its reachable nodes (BFS)
        distances = nx.single_source_shortest_path_length(G, selected_node)
        maxd = max(distances.values()) if distances else 1
        for i, n in enumerate(nodes):
            if n == selected_node:
                colors[i] = 'rgb(255,0,0)'
                sizes[i] = max_size
            elif n in distances:
                ratio = distances[n] / maxd
                r = 255
                g = int(165 * ratio)
                b = 0
                colors[i] = f"rgb({r},{g},{b})"
                sizes[i] = min_size + (max_size - min_size) * (1 - ratio) * 0.8

    node_trace = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers+text',
        text=[str(n) for n in nodes],
        textposition="top center",
        marker=dict(size=sizes, color=colors, line=dict(width=1, color='black')),
        hoverinfo="text",
        hovertext=[f"{n}<br>Eigenvector centrality: {centrality.get(n,0):.6f}" for n in nodes]
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Centralidad por vector propio (Eigenvector Centrality)",
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(xaxis=dict(showbackground=False),
                   yaxis=dict(showbackground=False),
                   zaxis=dict(showbackground=False))
    )
    return fig

def ranking_table_html(top_n=10):
    pairs = sorted([(n, centrality.get(n, 0.0)) for n in nodes], key=lambda x: -x[1])
    top = pairs[:top_n]
    rows = "".join([f"<tr><td>{i+1}</td><td>{p[0]}</td><td>{p[1]:.6f}</td></tr>" for i,p in enumerate(top)])
    html_table = f"""
    <table style="border-collapse: collapse; width: 100%;">
      <thead><tr><th>#</th><th>Nodo</th><th>Centralidad</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """
    return html_table

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Centralidad (Eigenvector)"),
    html.Div([
        html.Label("Resaltar top k nodos por centralidad:"),
        dcc.Input(id="input-topk", type="number", value=5, min=0, step=1),
        html.Span("  "),
        html.Label("Mostrar top en tabla:"),
        dcc.Input(id="input-tablen", type="number", value=10, min=1, step=1)
    ], style={"marginBottom": "10px"}),
    dcc.Graph(id="centrality-graph", figure=build_figure()),
    html.H3("Ranking (top n)"),
    html.Div(id="ranking-html", children=ranking_table_html(10)),
    html.Div(id="selected-info", style={"marginTop": "10px", "fontSize": "16px"})
])

@app.callback(
    [Output("centrality-graph", "figure"),
     Output("ranking-html", "children"),
     Output("selected-info", "children")],
    [Input("input-topk", "value"),
     Input("input-tablen", "value"),
     Input("centrality-graph", "clickData")]
)
def update(topk, tablen, clickData):
    selected = None
    if clickData and "points" in clickData and len(clickData["points"]) > 0:
        selected = clickData["points"][0].get("text")
    fig = build_figure(highlight_top_k=(topk or 0), selected_node=selected)
    table_html = ranking_table_html(top_n=(tablen or 10))
    info = "Haz clic en un nodo para ver detalle."
    if selected is not None:
        outdeg = G.out_degree(selected)
        paths = nx.single_source_shortest_path_length(G, selected)
        maxd = max(paths.values()) if paths else 0
        info = f"Nodo seleccionado: {selected} | Out-degree: {outdeg} | Grado máximo alcanzable: {maxd}"
    return fig, table_html, info

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
