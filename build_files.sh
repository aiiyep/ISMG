#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput --clear

# Faz as migrações
python manage.py migrate --noinput

#!/bin/bash

echo "🔨 BUILD INICIADO"

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verificar se a pasta foi criada
echo "✅ Verificando estrutura:"
ls -la staticfiles_build/ || echo "❌ Pasta staticfiles_build não encontrada!"
ls -la staticfiles_build/static/ || echo "❌ Pasta static não encontrada!"

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

echo "✅ BUILD CONCLUÍDO!"