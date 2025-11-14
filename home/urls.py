from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('workshops/', views.workshops, name='workshops'),
    path('workshops/inscricao/', views.workshop_inscricao, name='workshop_inscricao'),
    path('voluntariado/', views.voluntariado, name='voluntariado'),
    path('voluntariado/candidatura/', views.voluntariado_candidatura, name='voluntariado_candidatura'),
    path('newsletter/inscricao/', views.newsletter_inscricao, name='newsletter_inscricao'),
    # ✅ NOVA URL PARA DETALHES DA NOTÍCIA
    path('noticia/<int:id>/', views.noticia_detalhe, name='noticia_detalhe'),
    path('contato/', views.contato, name='contato'),
    path('doacao/', views.doacao, name='doacao'),
]