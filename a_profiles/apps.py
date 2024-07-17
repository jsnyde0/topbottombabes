from django.apps import AppConfig


class AProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a_profiles'

    def ready(self):
        import a_profiles.signals #noqa
