#!/usr/bin/env bash
# start.sh

# Navegar para o diretório do backend
cd backend

# Usar a variável PORT definida pelo ambiente, com fallback para 8000
PORT="${PORT:-8000}"

# Iniciar a aplicação com gunicorn (exec substitui o shell, bom para sinais)
CMD=(gunicorn --bind "0.0.0.0:$PORT" app.wsgi:application --workers 3 --threads 2 --timeout 120)

echo "Starting with PORT=$PORT"
echo "Command: ${CMD[*]}"

exec "${CMD[@]}"