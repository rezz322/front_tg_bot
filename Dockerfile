# Використовуємо офіційний образ Python 3.14 (slim версія для економії місця)
FROM python:3.14-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності (якщо потрібні для Prisma або мережевих інструментів)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо залежності Python
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код бота в контейнер
COPY . .

# Якщо ви використовуєте Prisma у Python (генеримо клієнт)
# RUN prisma generate

# Запускаємо бота (припускаємо, що головний файл — main.py)
CMD ["python", "main.py"]
