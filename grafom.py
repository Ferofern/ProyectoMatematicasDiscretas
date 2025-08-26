import networkx as nx
import csv
import plotly.graph_objects as go

# Listas para guardar remitentes y destinatarios
enviados = []
recibidos = []

# Abrir CSV separado por ;
with open('C:/Users/ferof/Downloads/DatasetRelaciones.csv', newline='', encoding='latin-1') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        if len(row) >= 2:
            enviados.append(row[0].strip())
            recibidos.append(row[1].strip())

# Crear grafo dirigido
G = nx.DiGraph()
for i in range(len(enviados)):
    if enviados[i] and recibidos[i]:
        G.add_edge(enviados[i], recibidos[i])

# Layout 3D
pos = nx.spring_layout(G, dim=3, seed=42)

# Coordenadas nodos
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]

# Calcular grados de salida ajustados (-1)
out_degrees = {n: max(G.out_degree(n) - 1, 0) for n in G.nodes()}

# Aristas
edge_x, edge_y, edge_z = [], [], []
for edge in G.edges():
    x0, y0, z0 = pos[edge[0]]
    x1, y1, z1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

edge_trace = go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode='lines',
    line=dict(color='gray', width=2),
    hoverinfo='none'
)

# Nodos con tooltip de aristas de salida
node_trace = go.Scatter3d(
    x=x_nodes, y=y_nodes, z=z_nodes,
    mode='markers+text',
    text=[str(node) for node in G.nodes()],  # etiqueta sobre nodo
    textposition="top center",
    marker=dict(size=8, color='skyblue', line=dict(width=1, color='black')),
    hoverinfo="text",
    hovertext=[f"Nodo: {node}<br>Aristas salida ajustadas: {out_degrees[node]}" for node in G.nodes()]
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    title="Grafo Dirigido en 3D (con hover info)",
    showlegend=False,
    margin=dict(l=0, r=0, b=0, t=40),
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=False)
    )
)

# 👉 Abre en navegador
fig.show(renderer="browser")
