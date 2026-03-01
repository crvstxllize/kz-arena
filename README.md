# KZ Arena

## О проекте
KZ Arena — учебный новостной портал о спорте и киберспорте Казахстана. Проект объединяет публичный сайт с лентой новостей и сущностями команд/турниров/матчей, роль Editor с dashboard для управления контентом, AJAX-интерактивы и JSON API без DRF.

## Стек
- Python + Django
- SQLite (dev/fallback) / PostgreSQL (поддерживается через env)
- HTML/CSS/JavaScript
- AJAX (`fetch`) для интерактивов
- JSON API (`JsonResponse`, без DRF)

## Функционал
- Новости: главная лента, фильтры, поиск, сортировка по популярности, пагинация, детальная статья
- Команды / турниры / матчи: списки и детальные страницы
- Accounts + роли: User / Editors / Admin
- Dashboard редактора: CRUD статей, публикация, медиа
- Django Admin: кастомизированный интерфейс управления моделями
- AJAX interactions: лайки/дизлайки, избранное, подписки, комментарии
- JSON API: публичные и защищённые endpoint-ы

## Быстрый старт

### 1) Клонирование
```bash
git clone <your-repo-url>
cd arena
```

### 2) Виртуальное окружение
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Зависимости
```bash
pip install -r requirements.txt
```

### 4) Переменные окружения
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

### 5) Миграции + bootstrap
```bash
python manage.py migrate
python manage.py bootstrap_all --seed
```

### 5.1) Создание суперпользователя (опционально, для admin)
```bash
python manage.py createsuperuser
```

### 6) Запуск
```bash
python manage.py runserver
```

Открыть: `http://127.0.0.1:8000/`

### Тестовые логины (после `bootstrap_all --seed`)
- Editor: `demo_editor` / `DemoPass123!`
- User: `demo_user_1` / `DemoPass123!`
- User: `demo_user_2` / `DemoPass123!`
- User: `demo_user_3` / `DemoPass123!`
- User: `demo_user_4` / `DemoPass123!`

## Переменные окружения

| Переменная | Обязательна | Пример | Назначение |
|---|---|---|---|
| `SECRET_KEY` | Да (обязательно при `DEBUG=0`) | `change-me` | Секрет Django |
| `DEBUG` | Да | `1` / `0` | Режим разработки/production |
| `ENV_NAME` | Нет | `dev` / `prod` | Метка окружения |
| `DB_ENGINE` | Нет | `sqlite` / `postgres` | Выбор БД (по умолчанию SQLite) |
| `DB_NAME` | Да для Postgres | `kz_arena` | Имя БД PostgreSQL |
| `DB_USER` | Да для Postgres | `postgres` | Пользователь PostgreSQL |
| `DB_PASSWORD` | Да для Postgres | `secret` | Пароль PostgreSQL |
| `DB_HOST` | Нет | `127.0.0.1` | Хост PostgreSQL |
| `DB_PORT` | Нет | `5432` | Порт PostgreSQL |
| `ALLOWED_HOSTS` | Да | `127.0.0.1,localhost` | Разрешённые хосты (CSV) |
| `CSRF_TRUSTED_ORIGINS` | Нет | `https://your-domain.com` | Доверенные origin для CSRF (CSV) |
| `USE_HTTPS` | Нет | `0` / `1` | Включает secure cookies в `DEBUG=0` |
| `SECURE_SSL_REDIRECT` | Нет | `0` / `1` | Принудительный редирект на HTTPS |
| `LOG_LEVEL` | Нет | `DEBUG` / `INFO` | Уровень логирования |

## Static и Media

- Dev (`DEBUG=1`): статика берётся из `static/` через `STATICFILES_DIRS`.
- Production (`DEBUG=0`): перед запуском выполнить:

```bash
python manage.py collectstatic
```

- Собранная статика попадает в `staticfiles/` и должна раздаваться веб-сервером/платформой.
- Медиа-файлы (например, `Article.cover`) хранятся в `media/` (`MEDIA_ROOT`).
- Favicon подключен через Django static: `static/img/favicon.svg` -> `templates/base.html`.

### Переключение БД: SQLite / PostgreSQL

По умолчанию проект работает на SQLite (`DB_ENGINE=sqlite`).

Для PostgreSQL укажите в `.env`:

```env
DB_ENGINE=postgres
DB_NAME=kz_arena
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

После переключения БД:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py bootstrap_all --seed
```

## Логи приложения

- Логи пишутся в консоль через стандартный `LOGGING` в `kz_arena/settings.py`.
- Уровень логирования регулируется env-переменной `LOG_LEVEL` (`DEBUG`, `INFO`, ...).
- Проверка локально:

```bash
python manage.py runserver
```

Смотреть вывод в том же терминале.

## Deploy на Render

Для проекта подготовлен blueprint:
- [render.yaml](/Users/nurserik/Desktop/kz-arena/render.yaml)

Что уже учтено:
- `gunicorn` для запуска Django в production
- `WhiteNoise` для раздачи `staticfiles`
- persistent disk для `media/`
- PostgreSQL в том же регионе
- поддержка custom domain через `PRIMARY_DOMAIN`

### Рекомендуемая конфигурация Render
- Web Service: `Starter`
- Region: `Frankfurt`
- Database: `basic-256mb` или выше
- Persistent Disk: `2 GB`, mount path:

```bash
/opt/render/project/src/media
```

### Если создаёте сервис вручную

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Start Command:

```bash
gunicorn kz_arena.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

### Обязательные env vars

Минимум:

```env
ENV_NAME=prod
DEBUG=0
SECRET_KEY=<generated>
USE_HTTPS=1
SECURE_SSL_REDIRECT=1
SERVE_MEDIA=1
LOG_LEVEL=INFO
PRIMARY_DOMAIN=your-domain.com
DB_ENGINE=postgres
DB_NAME=<from render postgres>
DB_USER=<from render postgres>
DB_PASSWORD=<from render postgres>
DB_HOST=<from render postgres>
DB_PORT=5432
```

Примечания:
- `PRIMARY_DOMAIN` автоматически добавляется в `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`
- Render hostname (`RENDER_EXTERNAL_HOSTNAME`) тоже подхватывается автоматически
- пример локального/production env вынесен в `.env.example`

## Линтинг и форматирование (минимальная настройка)

В проект добавлена минимальная конфигурация `black` и `isort` в `pyproject.toml`.

Команды:

```bash
black .
isort .
```

Примечание: не запускайте массовое форматирование перед защитой без отдельного коммита.

## Оптимизация ассетов (минимум)

- Для изображений используйте разумный размер (лого обычно 300-600px по ширине).
- Upload-изображения ограничены по расширению (`jpg/jpeg/png/webp`) и размеру (до 5MB).
- Перед защитой проверьте `static/` и `media/` на крупные неиспользуемые файлы.

### Логотипы команд (офлайн)

Лого команд хранятся локально в репозитории:
- `static/teams/logos/`

Маппинг имени команды к файлу задаётся в:
- `teams/assets.py`

После обновления ассетов/маппинга синхронизируйте значения `Team.logo` в БД:

```bash
python manage.py sync_team_logos
```

Полезные режимы:
- бережное обновление (по умолчанию): заполняет только пустые/битые `logo`
- принудительное обновление:

```bash
python manage.py sync_team_logos --force
```

Как добавить новое лого:
1. Положить файл в `static/teams/logos/` (рекомендуемо 300-600px по ширине).
2. Добавить соответствие в `teams/assets.py`.
3. Выполнить `python manage.py sync_team_logos`.

## API

Формат ответов:
- успех: `{ "ok": true, "data": ... }`
- ошибка: `{ "ok": false, "error": { "code": "...", "message": "...", "details": ... } }`

Публичные endpoint-ы:
- `GET /api/articles/`
- `GET /api/articles/<slug:slug>/`
- `GET /api/teams/`
- `GET /api/tournaments/`
- `GET /api/search/?q=...`

Защищённые endpoint-ы (Editor/staff):
- `POST /api/articles/`
- `PUT /api/articles/<int:pk>/`
- `DELETE /api/articles/<int:pk>/`

### Фильтры API (query params)

#### `GET /api/articles/`

Поддерживаемые параметры:
- `q` — поиск по `title`, `excerpt`, `content`, `author.username`
- `category` — slug категории
- `tag` — slug тега
- `kind` — тип контента (`sport` / `esport`)
- `discipline` — дисциплина (например `football`, `cs2`, `dota2`, `pubg`)
- `ordering` — сортировка: `new` (по умолчанию) или `popular` (по `views_count`)
- `page` — номер страницы (число, минимум `1`)
- `page_size` — размер страницы (число, `1..50`)

Примеры:

```bash
curl "http://127.0.0.1:8000/api/articles/?q=KZ&category=kibersport&ordering=popular&page=1&page_size=5"
```

```bash
curl "http://127.0.0.1:8000/api/articles/?kind=esport&discipline=cs2&tag=cs2"
```

#### `GET /api/teams/`

Поддерживаемые параметры:
- `kind` — тип (`sport` / `esport`)
- `discipline` — дисциплина

Пример:

```bash
curl "http://127.0.0.1:8000/api/teams/?kind=esport&discipline=cs2"
```

#### `GET /api/tournaments/`

Поддерживаемые параметры:
- `kind` — тип (`sport` / `esport`)
- `discipline` — дисциплина

Пример:

```bash
curl "http://127.0.0.1:8000/api/tournaments/?kind=sport&discipline=football"
```

#### `GET /api/search/`

Поддерживаемые параметры:
- `q` — строка поиска (минимум 2 символа)

Пример:

```bash
curl "http://127.0.0.1:8000/api/search/?q=astana"
```

Примеры:

```bash
curl "http://127.0.0.1:8000/api/articles/?ordering=popular&page=1&page_size=10"
```

```bash
curl "http://127.0.0.1:8000/api/search/?q=KZ"
```

```bash
curl -X POST "http://127.0.0.1:8000/api/articles/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API draft: тестовая статья",
    "content": "Текст статьи из API",
    "kind": "esport",
    "discipline": "cs2",
    "status": "draft",
    "category_slugs": ["kibersport"],
    "tag_slugs": ["cs2"]
  }'
```

## Deploy guide (общий)

1. Подготовить `.env` на сервере (не хранить в git):
- `DEBUG=0`
- `ENV_NAME=prod`
- `SECRET_KEY=<strong-random-secret>`
- `ALLOWED_HOSTS=your-domain.com,www.your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com`
- `USE_HTTPS=1`
- `SECURE_SSL_REDIRECT=1` (только если HTTPS уже настроен)

2. Установить зависимости и выполнить миграции:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

3. Собрать статику:
```bash
python manage.py collectstatic --noinput
```

4. Запустить bootstrap:
```bash
python manage.py bootstrap_all
```

5. Настроить веб-сервер/платформу:
- раздача `staticfiles/`
- раздача `media/` (если нужно)
- проксирование к Django (gunicorn/uvicorn + reverse proxy)

6. Мониторинг и диагностика (пример, если используете `systemd`):
- логи: `journalctl -u kz-arena -f`
- статус сервиса: `sudo systemctl status kz-arena`
- перезапуск: `sudo systemctl restart kz-arena`

7. Резервное копирование (минимальная стратегия):
- ежедневный дамп БД (для PostgreSQL через `pg_dump`)
- хранить последние 7 копий
- отдельно архивировать `media/`

Пример дампа:
```bash
pg_dump -h 127.0.0.1 -U postgres kz_arena > backup_$(date +%F).sql
```

## Учебная защита: что показать
- Главная страница и раздел новостей
- Фильтры/поиск/сортировка в `/news/`
- Детальная статья и рост просмотров
- AJAX: like/favorite/comments
- Dashboard Editor: создать и опубликовать статью
- Admin: inline assets и actions publish/unpublish
- API: `/api/articles/` и `/api/search/`

## Команды для быстрой проверки
```bash
python manage.py check
python manage.py migrate
python manage.py bootstrap_all --seed
python manage.py runserver
```

Prod-like локально:

macOS/Linux:
```bash
DEBUG=0 python manage.py runserver
```

Windows PowerShell:
```powershell
$env:DEBUG="0"; python manage.py runserver
```

## Smoke test
Подробный сценарий: `docs/SMOKE_TEST.md`
