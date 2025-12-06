# YaMDb API

## Описание проекта

**YaMDb** (Yet another Movie Database) — это REST API для сбора отзывов пользователей на различные произведения (фильмы, книги, музыкальные треки). Проект позволяет пользователям оставлять отзывы и оценки произведениям, комментировать отзывы других пользователей, а также управлять каталогом произведений.

### Основные функции

- **Управление пользователями**: Регистрация, аутентификация через JWT-токены, управление профилями
- **Каталог произведений**: Создание и управление произведениями с категориями (Фильмы, Книги, Музыка) и жанрами
- **Система отзывов**: Пользователи могут оставлять отзывы с оценкой (от 1 до 10) на произведения
- **Комментарии**: Возможность комментировать отзывы других пользователей
- **Рейтинговая система**: Автоматический расчет рейтинга произведения на основе оценок в отзывах
- **Роли и права доступа**: Система ролей (пользователь, модератор, администратор) с различными уровнями доступа
- **Фильтрация и поиск**: Поиск и фильтрация произведений по различным параметрам

### Пользовательские роли

- **Аноним** — может просматривать описания произведений, читать отзывы и комментарии
- **Аутентифицированный пользователь** (`user`) — может публиковать отзывы и ставить оценки, комментировать чужие отзывы, редактировать и удалять свои отзывы и комментарии
- **Модератор** (`moderator`) — те же права, что и у аутентифицированного пользователя, плюс право удалять любые отзывы и комментарии
- **Администратор** (`admin`) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры, назначать роли пользователям
- **Суперюзер Django** — обладает правами администратора

## Технологический стек

### Backend
- **Python 3.9+**
- **Django 3.2** — веб-фреймворк
- **Django REST Framework 3.12.4** — для создания REST API
- **djangorestframework-simplejwt 4.8.0** — JWT-аутентификация
- **django-filter 2.4.0** — фильтрация данных

### База данных
- **SQLite3** — база данных по умолчанию (для разработки)

### Тестирование
- **pytest 6.2.4** — фреймворк для тестирования
- **pytest-django 4.4.0** — интеграция pytest с Django

### Документация
- **ReDoc** — интерактивная документация API (доступна по адресу `/redoc/`)

## Установка и развертывание

### Предварительные требования

- Python 3.9 или выше
- pip (менеджер пакетов Python)
- Git (для клонирования репозитория)

### Шаги по установке

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd api_yamdb
   ```

2. **Создайте и активируйте виртуальное окружение:**
   
   Для Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   Для Linux/MacOS:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Выполните миграции базы данных:**
   ```bash
   cd api_yamdb
   python manage.py migrate
   ```

5. **Создайте суперпользователя (опционально):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
   ```

После выполнения этих шагов API будет доступен по адресу `http://127.0.0.1:8000/`

### Загрузка тестовых данных (опционально)

В проекте есть CSV-файлы с тестовыми данными в директории `api_yamdb/static/data/`. Для их загрузки можно использовать Django management команды или скрипты.

## Настройка окружения

Проект использует настройки по умолчанию из файла `api_yamdb/api_yamdb/settings.py`. Для продакшн-окружения рекомендуется:

1. **Создать файл `.env`** в корне проекта (в директории `api_yamdb/`) со следующими переменными:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

2. **Использовать переменные окружения** в `settings.py`:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
   DEBUG = os.getenv('DEBUG', 'False') == 'True'
   ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
   ```

3. **Настроить базу данных** (для продакшна рекомендуется PostgreSQL):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DB_NAME'),
           'USER': os.getenv('DB_USER'),
           'PASSWORD': os.getenv('DB_PASSWORD'),
           'HOST': os.getenv('DB_HOST', 'localhost'),
           'PORT': os.getenv('DB_PORT', '5432'),
       }
   }
   ```

4. **Настроить отправку email** (для отправки кодов подтверждения):
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = os.getenv('EMAIL_HOST')
   EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
   EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
   EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
   ```

**Примечание:** В текущей версии проекта настройки хранятся напрямую в `settings.py`. Для продакшн-окружения обязательно вынесите чувствительные данные в переменные окружения.

## API Endpoints

Все запросы к API начинаются с префикса `/api/v1/`

### Аутентификация
- `POST /api/v1/auth/signup/` — Регистрация нового пользователя
- `POST /api/v1/auth/token/` — Получение JWT-токена

### Пользователи
- `GET /api/v1/users/` — Список всех пользователей (только для администратора)
- `GET /api/v1/users/me/` — Получение данных своей учетной записи
- `PATCH /api/v1/users/me/` — Изменение данных своей учетной записи
- `GET /api/v1/users/{username}/` — Получение пользователя по username
- `PATCH /api/v1/users/{username}/` — Изменение данных пользователя (администратор)
- `DELETE /api/v1/users/{username}/` — Удаление пользователя (администратор)

### Произведения
- `GET /api/v1/titles/` — Список всех произведений
- `POST /api/v1/titles/` — Добавление произведения (администратор)
- `GET /api/v1/titles/{id}/` — Информация о произведении
- `PATCH /api/v1/titles/{id}/` — Обновление произведения (администратор)
- `DELETE /api/v1/titles/{id}/` — Удаление произведения (администратор)

### Категории
- `GET /api/v1/categories/` — Список всех категорий
- `POST /api/v1/categories/` — Добавление категории (администратор)
- `DELETE /api/v1/categories/{slug}/` — Удаление категории (администратор)

### Жанры
- `GET /api/v1/genres/` — Список всех жанров
- `POST /api/v1/genres/` — Добавление жанра (администратор)
- `DELETE /api/v1/genres/{slug}/` — Удаление жанра (администратор)

### Отзывы
- `GET /api/v1/titles/{title_id}/reviews/` — Список всех отзывов на произведение
- `POST /api/v1/titles/{title_id}/reviews/` — Добавление отзыва (аутентифицированные пользователи)
- `GET /api/v1/titles/{title_id}/reviews/{review_id}/` — Получение отзыва
- `PATCH /api/v1/titles/{title_id}/reviews/{review_id}/` — Обновление отзыва (автор, модератор, администратор)
- `DELETE /api/v1/titles/{title_id}/reviews/{review_id}/` — Удаление отзыва (автор, модератор, администратор)

### Комментарии
- `GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/` — Список комментариев к отзыву
- `POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/` — Добавление комментария (аутентифицированные пользователи)
- `GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — Получение комментария
- `PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — Обновление комментария (автор, модератор, администратор)
- `DELETE /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — Удаление комментария (автор, модератор, администратор)

### Документация API

Интерактивная документация API доступна по адресу:
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

## Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос на `/api/v1/auth/signup/` с параметрами `email` и `username`
2. YaMDb отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный email
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на `/api/v1/auth/token/`
4. В ответе приходит JWT-токен для дальнейшей работы с API
5. При желании пользователь может отправить PATCH-запрос на `/api/v1/users/me/` для заполнения профиля

## Запуск тестов

Для запуска тестов используйте pytest:

```bash
cd api_yamdb
pytest
```

Для более подробного вывода:

```bash
pytest -vv
```

## Структура проекта

```
api_yamdb/
├── api_yamdb/          # Основная директория проекта
│   ├── api/            # API приложение
│   │   ├── users/      # Управление пользователями
│   │   ├── titles/     # Управление произведениями
│   │   └── reviews/    # Управление отзывами и комментариями
│   ├── api_yamdb/      # Настройки проекта
│   │   ├── settings.py # Конфигурация
│   │   └── urls.py     # Главный URL-конфиг
│   ├── reviews/         # Модели отзывов
│   ├── users/           # Модели пользователей
│   ├── static/          # Статические файлы (CSV данные, документация)
│   ├── templates/      # Шаблоны (ReDoc)
│   └── manage.py        # Django management скрипт
├── tests/               # Тесты проекта
├── postman_collection/  # Postman коллекция для тестирования API
├── requirements.txt     # Зависимости проекта
├── pytest.ini          # Конфигурация pytest
└── README.md           # Документация проекта
```

## Автор

@Ndk985