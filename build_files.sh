#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput --clear

# Faz as migrações
python manage.py migrate --noinput

#!/bin/bash

echo "🔨 Instalando dependências..."
pip install -r requirements.txt

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

echo "✅ Build concluído!"