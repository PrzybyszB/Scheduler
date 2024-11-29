from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # Django_q
    # def ready(self):
    #     from api.tasks_scheduler import start_task
    #     start_task()