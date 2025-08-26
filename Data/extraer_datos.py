import pandas as pd

def extraer_datos(path):
    df = pd.read_excel(path, header=0)
    enviados = df.iloc[:, 0].astype(str).str.strip().tolist()
    recibidos = df.iloc[:, 1].astype(str).str.strip().tolist()
    return enviados, recibidos
