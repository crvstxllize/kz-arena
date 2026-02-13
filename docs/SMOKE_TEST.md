# SMOKE TEST

Короткий сценарий ручной проверки перед защитой/деплоем.

## 1) Подготовка

```bash
python manage.py check
python manage.py migrate
python manage.py bootstrap_all --seed
python manage.py runserver
```

Открыть: `http://127.0.0.1:8000/`

## 2) Публичная часть

Проверить страницы:
- `/`
- `/news/`
- `/news/<slug>/` (любая существующая статья)
- `/teams/`
- `/tournaments/`
- `/matches/`
- `/about/`

Проверить:
- фильтры и поиск в `/news/`
- пагинацию в `/news/`
- рост `views_count` при первом открытии статьи

## 3) Accounts и роли

- Войти под editor/staff
- Проверить `/accounts/profile/`
- В navbar виден переход в Dashboard для Editor/staff

## 4) Dashboard

- Открыть `/dashboard/`
- Создать статью (draft)
- Опубликовать статью
- Проверить появление статьи на `/news/`

## 5) AJAX interactions

На `/news/<slug>/` проверить:
- like/dislike/favorite без перезагрузки
- добавление комментария
- удаление своего комментария

## 6) API

Проверить:
- `GET /api/articles/?ordering=popular`
- `GET /api/search/?q=KZ`
- `GET /api/teams/`
- `GET /api/tournaments/`

Под Editor/staff:
- `POST /api/articles/` (создание draft)
- `PUT /api/articles/<pk>/`
- `DELETE /api/articles/<pk>/`

Убедиться, что ошибки API всегда в формате:

```json
{
  "ok": false,
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```

## 7) Prod-like локальная проверка

macOS/Linux:

```bash
DEBUG=0 python manage.py runserver
```

Windows PowerShell:

```powershell
$env:DEBUG="0"; python manage.py runserver
```

Проверить:
- кастомные 404/500
- загрузку статики после `collectstatic`
