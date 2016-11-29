from django.apps import AppConfig


class ParkkihubiAppConfig(AppConfig):
    
    name = 'parkkihubi'

    def ready(self):
        pass  # You can add project-wide patches, signals, etc here!
