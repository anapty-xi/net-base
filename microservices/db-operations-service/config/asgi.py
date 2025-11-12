'''определение промежуточного слоя DBPoolMiddleware для инициализации и закрытия пула подключений в соответствии с состоянием сервера'''

import os
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

