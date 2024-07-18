from django.apps import AppConfig


class ACartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a_cart'

    # import signals
    def ready(self):
        import a_cart.signals
