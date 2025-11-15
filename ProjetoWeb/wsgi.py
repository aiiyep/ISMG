import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjetoWeb.settings')

application = get_wsgi_application()

# ✅ Adicione isso para o Vercel
app = application