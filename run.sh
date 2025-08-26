#!/bin/bash
# Ejecuta todas las interfaces Dash en paralelo y espera a que terminen

python3 -m UI.dash_app & 
python3 -m UI.grafo3d_dash & 
python3 -m UI.centralidad_dash & 
wait
