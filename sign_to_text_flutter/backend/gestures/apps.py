from django.apps import AppConfig


class GesturesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestures'
    verbose_name = 'Sign Language Gestures'
    
    def ready(self):
        # Import signal handlers if any
        pass
