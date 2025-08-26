import networkx as nx
import numpy as np
import plotly.graph_objects as go
from http.server import SimpleHTTPRequestHandler, HTTPServer
import plotly.io as pio
from Data.extraer_datos import extraer_datos

enviados, recibidos = extraer_datos('Data/DatasetRelaciones.xlsx')

G = nx.DiGraph()
for e, r in zip(enviados, recibidos):
    G.add_edge(e, r)

pos = nx.spring_layout(G, dim=3, seed=42)
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]

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
    vec = end - start
    vec_len = np.linalg.norm(vec)
    if vec_len == 0:
        continue
    vec_dir = vec / vec_len
    perp1 = np.cross(vec_dir, np.array([0, 0, 1]))
    if np.linalg.norm(perp1) < 1e-6:
        perp1 = np.cross(vec_dir, np.array([0, 1, 0]))
    perp1 = perp1 / np.linalg.norm(perp1)
    tip1 = end - vec_dir * arrow_size + 0.5 * arrow_size * perp1
    tip2 = end - vec_dir * arrow_size - 0.5 * arrow_size * perp1
    edge_traces.append(go.Mesh3d(
        x=[end[0], tip1[0], tip2[0]],
        y=[end[1], tip1[1], tip2[1]],
        z=[end[2], tip1[2], tip2[2]],
        color='skyblue',
        opacity=0.8,
        hoverinfo='none'
    ))

out_degrees = {n: max(G.out_degree(n) - 1, 0) for n in G.nodes()}
node_trace = go.Scatter3d(
    x=x_nodes, y=y_nodes, z=z_nodes,
    mode='markers+text',
    text=[str(node) for node in G.nodes()],
    textposition="top center",
    marker=dict(size=8, color='skyblue', line=dict(width=1, color='black')),
    hoverinfo="text",
    hovertext=[f"Nodo: {node}<br>Aristas salida ajustadas: {out_degrees[node]}" for node in G.nodes()]
)

fig = go.Figure(data=edge_traces + [node_trace])
fig.update_layout(
    title="Grafo Dirigido en 3D (flechas rellenas)",
    showlegend=False,
    margin=dict(l=0, r=0, b=0, t=40),
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=False)
    )
)

pio.write_html(fig, file='grafo.html', auto_open=False)

port = 8080
server_address = ("", port)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
print(f"Sirviendo en http://localhost:{port}/grafo.html")
httpd.serve_forever()
