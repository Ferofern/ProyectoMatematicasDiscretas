import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from MatrizAsociada.matriz import generar_matriz

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Matriz de Adyacencia y Potencia"),
    html.Label("Potencia k:"),
    dcc.Input(id="input-k", type="number", value=1, min=1, step=1),
    html.Br(), html.Br(),
    html.H2("Matriz de Adyacencia A"),
    dcc.Graph(id="heatmap-A"),
    html.H2("Matriz A^k (caminos posibles)"),
    dcc.Graph(id="heatmap-Ak"),
    html.H2("Grado del Grafo"),
    html.Div(id="grado-comparacion", style={"fontSize": "18px", "marginTop": "10px"})
])

@app.callback(
    [Output("heatmap-A", "figure"),
     Output("heatmap-Ak", "figure"),
     Output("grado-comparacion", "children")],
    [Input("input-k", "value")]
)
def update_matrices(k):
    A, nodes = generar_matriz()
    # Convertir A^k a 0/1 para indicar existencia de caminos
    if k == 1:
        Ak = A.copy()
    else:
        Ak = np.linalg.matrix_power(A, k)
        Ak = (Ak > 0).astype(int)  # 1 si hay al menos un camino de longitud k

    # Calcular grados
    grado_total_A = np.sum(A)       # suma de todos los elementos de A
    grado_total_Ak = np.sum(Ak)     # suma de todos los elementos de Ak
    comparacion_grados = f"Grado total en A: {grado_total_A}, Grado total en A^{k}: {grado_total_Ak}"


    # Crear Heatmaps
    fig_A = go.Figure(data=go.Heatmap(
        z=A,
        x=nodes,
        y=nodes,
        colorscale='Viridis',
        text=A.round(0),
        texttemplate="%{text}"
    ))
    fig_A.update_layout(title="Matriz A")

    fig_Ak = go.Figure(data=go.Heatmap(
        z=Ak,
        x=nodes,
        y=nodes,
        colorscale='Viridis',
        text=Ak,
        texttemplate="%{text}"
    ))
    fig_Ak.update_layout(title=f"Matriz A^{k} (existencia de caminos)")

    return fig_A, fig_Ak, comparacion_grados

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
