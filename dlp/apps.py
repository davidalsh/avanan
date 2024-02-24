from django.apps import AppConfig


class DlpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dlp'

    # def ready(self):
    #     manager = Manager()
    #     loop = asyncio.get_event_loop()
    #     loop.create_task(manager.main())
