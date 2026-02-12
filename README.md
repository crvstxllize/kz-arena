# KZ Arena

Новостной портал о спорте и киберспорте Казахстана на Django.

## Setup

1. Создайте и активируйте виртуальное окружение.

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

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте `.env` из примера:
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте базовые роли:
```bash
python manage.py bootstrap_roles
```

6. (Опционально) Создайте администратора:
```bash
python manage.py createsuperuser
```

7. Заполните проект демо-данными:
```bash
python manage.py seed_demo
```

8. Запустите сервер:
```bash
python manage.py runserver
```

## Environment variables

`.env.example` содержит:
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS` (через запятую)

## Accounts

Доступные маршруты:
- `/accounts/register/`
- `/accounts/login/`
- `/accounts/logout/` (POST)
- `/accounts/profile/`
- `/accounts/profile/edit/`
- `/accounts/password-change/`
- `/accounts/password-reset/` (заглушка)

`/accounts/password-reset/` пока отображает справочную страницу. Для реального восстановления пароля нужно настроить SMTP/email backend в `settings.py`.

## Demo data

Команда `python manage.py seed_demo` идемпотентна: повторный запуск обновляет/дополняет фиксированный демо-набор и не создает бесконечные дубликаты.
