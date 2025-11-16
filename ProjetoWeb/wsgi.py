import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjetoWeb.settings')

application = get_wsgi_application()

# ✅ WhiteNoise para servir arquivos estáticos no Vercel
from whitenoise import WhiteNoise
application = WhiteNoise(application, root='/tmp')