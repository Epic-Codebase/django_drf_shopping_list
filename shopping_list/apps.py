from django.apps.config import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shopping_list"

    def ready(self):
        import shopping_list.receivers
