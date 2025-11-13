from django.urls import path
from . import views

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # Workshops
    path('workshops/', views.workshops, name='workshops'),
    path('workshops/inscricao/', views.workshop_inscricao, name='workshop_inscricao'),
    
    # Voluntariado
    path('voluntariado/', views.voluntariado, name='voluntariado'),
    path('voluntariado/candidatura/', views.voluntariado_candidatura, name='voluntariado_candidatura'),
    
    # Newsletter
    path('newsletter/inscricao/', views.newsletter_inscricao, name='newsletter_inscricao'),
]