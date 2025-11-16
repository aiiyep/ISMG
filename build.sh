#!/bin/bash

echo "🔨 Iniciando build..."

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

echo "✅ Build concluído!"