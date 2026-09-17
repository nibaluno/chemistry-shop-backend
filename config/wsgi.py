# """
# WSGI config for config project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = get_wsgi_application()


import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ЗАПУСК СИДЕРА ПРИ СТАРТЕ WSGI (Render поднимает сайт именно через этот файл)
try:
    import seed
    seed.run_seed()
    print("Сидинг при старте WSGI выполнен успешно!")
except Exception as e:
    print(f"Ошибка сидинга в WSGI: {e}")

application = get_wsgi_application()
