from django.apps import AppConfig
import sys

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Запускаем сидер только при реальной работе сервера (не при миграциях и тестах)
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv:
            try:
                import seed
                seed.run_seed()
            except Exception as e:
                print(f"Ошибка автозапуска seed: {e}")