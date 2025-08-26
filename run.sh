#!/bin/bash
# Script para instalar dependencias y correr ambas apps

echo "🔄 Instalando/actualizando dependencias..."
pip install -r requirements.txt

echo "🚀 Iniciando aplicaciones..."
python3 -m UI.dash_app & 
python3 -m UI.grafo3d_dash & 
wait
