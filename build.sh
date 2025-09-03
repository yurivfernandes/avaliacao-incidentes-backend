#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Navegar para o diretório do backend
cd backend

# Configurar variáveis para forçar IPv4
export PGHOST=${DB_HOST:-localhost}
export PGPORT=${DB_PORT:-5432}

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Executar migrações
python manage.py migrate