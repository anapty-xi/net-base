import os
from django.core.asgi import get_asgi_application
import django
from . import pool

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

class DBPoolMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    django.setup()
                    await pool.create_db_pool()
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    await pool.shutdown_pool()
                    await send({'type': 'lifespan.shutdown.complete'})
                    break
                else:
                    break
        else:
            await self.app(scope, receive, send)

application = DBPoolMiddleware(application)