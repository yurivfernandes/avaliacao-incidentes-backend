#!/usr/bin/env bash
# start.sh

# Navegar para o diretório do backend
cd backend

# Iniciar a aplicação com gunicorn
gunicorn --bind 0.0.0.0:$PORT app.wsgi:application