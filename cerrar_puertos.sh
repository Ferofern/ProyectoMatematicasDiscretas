#!/bin/bash
PUERTOS=(8080 8081 8082)
for PUERTO in "${PUERTOS[@]}"; do
    echo "Cerrando procesos en el puerto $PUERTO..."
    PID=$(lsof -ti tcp:$PUERTO)
    if [ -n "$PID" ]; then
        kill -9 $PID
        echo "Proceso $PID cerrado en el puerto $PUERTO"
    else
        echo "No hay procesos corriendo en el puerto $PUERTO"
    fi
done
echo "Todos los puertos especificados han sido verificados."
