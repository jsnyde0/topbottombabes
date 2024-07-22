from django.apps import AppConfig


class AOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a_orders'

    def ready(self):
        import a_orders.signals  # noqa
