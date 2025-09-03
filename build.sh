#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

# Instalar dependências
pip install -r requirements.txt

# Navegar para o diretório do backend
cd backend

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Executar migrações
python manage.py migrate