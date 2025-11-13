from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
    
    def ready(self):
        """
        Importa os signals quando a aplicação está pronta
        """
        import home.signals
        print("✅ Signals carregados com sucesso!")