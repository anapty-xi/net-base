📈 Market Price Tracker

Асинхронный сервис для мониторинга цен на Яндекс Маркете. Парсит цены на интересующие товары, сохраняет их и позволяет отследить историю цены.

🛠 Технологический стек

Backend: Python, FastAPI
Database: PostgreSQL 15 (+ asyncpg)
Bot: Aiogram 3.x, httpx
Parsing: Playwright (Chromium), playwright_stealth
Task Management: Redis
Infrastructure: Docker, Docker Compose
Logging: Loguru

🚀 Ключевые особенности
1. Async Everything: Полностью асинхронная архитектура от эндпоинтов до запросов к БД.
2. Использование playwright_stealth, позволяет отправлять запросы эффективнее без получение капчи
3. Dockerized Secrets: Безопасное управление конфиденциальными данными через Docker Secrets.
4. Clean Architecture + type hints для обеспечения легкого маштабирования и последущей разработки
5. Авто тесты позволяют изменять части сервиса и автоматически проверять их (в ближайшем будущем)

