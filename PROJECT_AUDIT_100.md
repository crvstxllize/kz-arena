# Project Audit — 100 points checklist

Дата аудита: 2026-02-18

## A) Определение стека
- Стек проекта: **Django (Python) + SQLite + HTML/CSS/JS + JSON API без DRF**.
- Вывод: проект **Django**, требования чеклиста применимы напрямую (с адаптацией предметной области: не библиотека, а спорт/киберспорт новости).

## B) Карта репозитория
- `kz_arena/` — глобальные настройки проекта (`settings.py`, `urls.py`, WSGI).
- `core/` — главная/о проекте/ошибки 404/500, служебные модели и management-команды bootstrap/seed.
- `accounts/` — регистрация, логин/логаут, профиль, смена пароля, заглушка reset.
- `articles/` — новости (модель, список/деталь, фильтры, пагинация, поиск, templatetags).
- `teams/` — команды и игроки, списки/детали, лого, templatetags.
- `tournaments/` — турниры/матчи/результаты, списки/детали.
- `comments/` — комментарии (AJAX add/delete/list).
- `interactions/` — лайки/дизлайки/избранное/подписки (AJAX).
- `taxonomy/` — категории/теги.
- `dashboard/` — editor/staff CRUD по новостям.
- `api/` — JSON API (`/api/...`) с валидацией и единым форматом ошибок.
- `templates/` — Django шаблоны (`base.html`, страницы и include-компоненты).
- `static/` — CSS/JS/изображения/плейсхолдеры/лого команд.
- `media/` — uploaded media (cover/logo/avatar и др.).
- `docs/` — smoke test сценарий.

## C) Команды запуска/деплоя
- Локальный запуск:
  - `python3 -m venv .venv` / `source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `cp .env.example .env`
  - `python manage.py migrate`
  - `python manage.py bootstrap_all --seed`
  - `python manage.py runserver`
- Проверка:
  - `venv/bin/python manage.py check`
- Production/деплой (описано в README):
  - `DEBUG=0`, `ENV_NAME=prod`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
  - `python manage.py migrate`
  - `python manage.py collectstatic --noinput`

## Quick start
- Python: 3.9 (по текущему venv).
- Зависимости: `requirements.txt`.
- Env: `.env` на основе `.env.example`.
- База: локально `db.sqlite3` (в `kz_arena/settings.py`).
- Demo-аккаунты после `bootstrap_all --seed`:
  - `demo_editor` / `DemoPass123!`
  - `demo_user_1` / `DemoPass123!`
  - `demo_user_2` / `DemoPass123!`
  - `demo_user_3` / `DemoPass123!`
  - `demo_user_4` / `DemoPass123!`

---

## 1. Основы и структура проекта

### 1.1 Django запускается локально и предусмотрен прод-режим (`DEBUG=False`)
- Статус: ✅ выполнено
- Где в коде: `manage.py`, `kz_arena/settings.py`, `README.md`
- Как показать преподавателю:
  - В VSCode открыть `kz_arena/settings.py` (блок `DEBUG`, `ENV_NAME`, `SECRET_KEY`).
  - В терминале: `venv/bin/python manage.py check`.
  - Запустить `DEBUG=0 venv/bin/python manage.py runserver`.

### 1.2 Минимум 10 приложений + AppConfig
- Статус: ✅ выполнено
- Где в коде: `kz_arena/settings.py` (`INSTALLED_APPS`), `accounts/apps.py`, `api/apps.py`, `articles/apps.py`, `comments/apps.py`, `core/apps.py`, `dashboard/apps.py`, `interactions/apps.py`, `taxonomy/apps.py`, `teams/apps.py`, `tournaments/apps.py`
- Как показать преподавателю:
  - Открыть `kz_arena/settings.py` и перечислить 10 доменных apps.
  - Открыть по одному `apps.py` с `AppConfig`.

### 1.3 Настроены settings/env, urls include+namespace, templates/static
- Статус: ✅ выполнено
- Где в коде: `kz_arena/settings.py`, `kz_arena/urls.py`
- Как показать преподавателю:
  - В `settings.py`: `load_dotenv`, `TEMPLATES`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_ROOT`.
  - В `urls.py`: `include(..., namespace=...)`.

### 1.4 Базовый layout (header/footer/menu/active)
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `templates/includes/navbar.html`, `templates/includes/footer.html`
- Как показать преподавателю:
  - Открыть `base.html` (include navbar/footer).
  - В браузере перейти `/`, `/news/`, `/teams/` и показать активный пункт меню.

### 1.5 Кастомные 404/500
- Статус: ✅ выполнено
- Где в коде: `kz_arena/urls.py`, `core/views.py`, `templates/core/404.html`, `templates/core/500.html`
- Как показать преподавателю:
  - В VSCode показать `handler404/handler500`.
  - В браузере открыть несуществующий URL для 404.

### 1.6 README (установка, миграции, суперпользователь, домен, тест-логины)
- Статус: ✅ выполнено (кроме фактического прод-домена, см. 9.1)
- Где в коде: `README.md`
- Как показать преподавателю:
  - Открыть в `README.md` quick start, env, superuser, static/collectstatic, deploy и тестовые логины.

### 1.7 Git hygiene: осмысленные коммиты, .gitignore, requirements, .env.example
- Статус: ✅ выполнено
- Где в коде: `.gitignore`, `requirements.txt`, `.env.example`, история коммитов (`git log --oneline`)
- Как показать преподавателю:
  - Открыть эти файлы.
  - Показать ленту коммитов и 5 новых осмысленных коммитов по фиксам чеклиста.

### 1.8 Линтинг/форматирование
- Статус: ✅ выполнено
- Где в коде: `pyproject.toml`, `README.md`
- Как показать преподавателю:
  - Открыть `pyproject.toml` (black/isort) и команды в `README.md`.

### 1.9 Логи без утечки секретов
- Статус: ✅ выполнено
- Где в коде: `kz_arena/settings.py` (`LOGGING`)
- Как показать преподавателю:
  - Открыть `LOGGING` в `settings.py`.
  - Запустить сервер и показать логи в консоли.

---

## 2. Дизайн + HTML + CSS + JS

### 2.1 Дизайн на базе бесплатного интернет-шаблона
- Статус: ❌ нет (не зафиксировано доказательство)
- Где в коде: в репозитории нет ссылки/папки-источника шаблона
- Как показать преподавателю:
  - Сейчас показать нечего как подтверждение происхождения шаблона.
- Минимальный план фикса:
  - Добавить в `README.md` раздел “Template source” с URL шаблона, лицензией и перечнем ваших доработок.

### 2.2 HTML5/семантика главной
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `templates/core/home.html`
- Как показать преподавателю:
  - Открыть `base.html` (`header/main/footer`) и `home.html` (`section/article/aside`).

### 2.3 Единая дизайн-система
- Статус: ✅ выполнено
- Где в коде: `static/css/style.css` (CSS variables, общие компоненты `.button`, `.news-card`, `.section`)
- Как показать преподавателю:
  - Показать `:root` и повторное использование классов.

### 2.4 Минимум 15 UI-страниц
- Статус: ✅ выполнено
- Где в коде: `templates/` (страниц существенно больше 15)
- Как показать преподавателю:
  - Показать список файлов в `templates/` и открыть ключевые: home/news detail/profile/dashboard/teams/tournaments/matches.

### 2.5 Адаптивность (3 брейкпоинта)
- Статус: ✅ выполнено
- Где в коде: `static/css/style.css` (`@media` для mobile/tablet/desktop)
- Как показать преподавателю:
  - DevTools: режимы mobile/tablet/desktop на `/news/`.

### 2.6 15+ CSS-эффектов
- Статус: ✅ выполнено
- Где в коде: `static/css/style.css` (hover/transition/focus/modal/animation/live pulse и др.)
- Как показать преподавателю:
  - На странице продемонстрировать hover карточек, модалку share, theme toggle, live badge animation.

### 2.7 15+ JS-сценариев
- Статус: ✅ выполнено
- Где в коде: `static/js/main.js` (15 инициализаторов: меню, тема, автокомплит, load more, interactions, comments ajax и др.)
- Как показать преподавателю:
  - Открыть `main.js` и блок `DOMContentLoaded`.
  - В браузере пройтись по сценариям.

### 2.8 Static через `static/`
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `templates/includes/*`, `articles/templatetags/news_media.py`, `teams/templatetags/team_media.py`
- Как показать преподавателю:
  - Показать `{% load static %}` и пути `{% static 'css/style.css' %}`.

### 2.9 Оптимизация ассетов (без мусора)
- Статус: ✅ выполнено
- Где в коде: `static/`, `README.md`
- Как показать преподавателю:
  - Показать структуру `static/` и раздел “Оптимизация ассетов” в `README.md`.

### 2.10 Доступность (alt/focus/не только цвет)
- Статус: ✅ выполнено
- Где в коде: `templates/**/*.html` (`alt` у img), `static/css/style.css` (`:focus-visible`), `templates/includes/navbar.html` (ARIA)
- Как показать преподавателю:
  - Табом пройти меню/кнопки.
  - Показать alt в `templates/includes/news_card.html`.

---

## 3. Пользователи, роли и формы

### 3.1 Регистрация GET/POST + валидация + messages
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `accounts/forms.py`, `templates/accounts/register.html`
- Как показать преподавателю:
  - Зарегистрировать пользователя и показать success/error messages.

### 3.2 Логин/логаут + CSRF + next=
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `templates/accounts/login.html`, `templates/includes/navbar.html`
- Как показать преподавателю:
  - Открыть `/accounts/login/?next=/dashboard/`, войти и показать редирект.

### 3.3 Профиль просмотр/редактирование
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `accounts/forms.py`, `templates/accounts/profile.html`, `templates/accounts/profile_edit.html`
- Как показать преподавателю:
  - Обновить имя/email в `/accounts/profile/edit/`.

### 3.4 Роли/права минимум 3 роли
- Статус: ✅ выполнено
- Где в коде: `dashboard/decorators.py`, `api/decorators.py`, `core/management/commands/seed_demo.py`
- Как показать преподавателю:
  - user не видит dashboard, editor/staff видит и может CRUD.

### 3.5 Смена пароля + reset по email/заглушка
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `templates/accounts/password_change.html`, `templates/accounts/password_reset_stub.html`
- Как показать преподавателю:
  - Показать форму смены пароля и страницу reset-заглушки.

### 3.6 CRUD формы на Django Forms/ModelForms
- Статус: ✅ выполнено
- Где в коде: `dashboard/forms.py`, `dashboard/views.py`
- Как показать преподавателю:
  - Создать/изменить/удалить статью в `/dashboard/articles/`.

### 3.7 Защита от дублей (unique + понятные сообщения)
- Статус: ✅ выполнено
- Где в коде: `accounts/forms.py` (`clean_email`), `articles/models.py` (`slug unique`), `interactions/models.py` (`UniqueConstraint`)
- Как показать преподавателю:
  - Попробовать зарегистрировать существующий email.

### 3.8 Пагинация с сохранением фильтров
- Статус: ✅ выполнено
- Где в коде: `articles/views.py`, `templates/articles/news_list.html`, `teams/views.py`, `tournaments/views.py`
- Как показать преподавателю:
  - Применить фильтр на `/news/`, перейти на следующую страницу и показать querystring.

---

## 4. ORM, модели и связи

### 4.1 Модели (>=15 в домене)
- Статус: ✅ выполнено
- Где в коде: `accounts/models.py`, `articles/models.py`, `comments/models.py`, `core/models.py`, `interactions/models.py`, `taxonomy/models.py`, `teams/models.py`, `tournaments/models.py`
- Как показать преподавателю:
  - Кратко перечислить модели в этих файлах.

### 4.2 Связи FK/M2M/O2O
- Статус: ✅ выполнено
- Где в коде: `articles/models.py`, `tournaments/models.py`, `interactions/models.py`, `accounts/models.py`
- Как показать преподавателю:
  - Открыть примеры: `Article.categories (M2M)`, `Match.tournament (FK)`, `MatchResult.match (O2O)`.

### 4.3 CRUD через ORM + проверки прав
- Статус: ✅ выполнено
- Где в коде: `dashboard/views.py`, `api/views.py`
- Как показать преподавателю:
  - Попробовать edit/delete статьи как владелец и как обычный user.

### 4.4 Slug и человекочитаемые URL
- Статус: ✅ выполнено
- Где в коде: `core/utils.py`, `articles/models.py`, `teams/models.py`, `tournaments/models.py`, `taxonomy/models.py`
- Как показать преподавателю:
  - Показать URL вида `/news/<slug>/`.

### 4.5 Индексация/оптимизация (`ordering`, `select_related`/`prefetch_related`)
- Статус: ✅ выполнено
- Где в коде: `articles/models.py`, `tournaments/models.py`, `comments/models.py`, `articles/views.py`, `api/views.py`
- Как показать преподавателю:
  - В коде показать `indexes` + `select_related/prefetch_related`.

### 4.6 Фильтрация/поиск/сортировка
- Статус: ✅ выполнено
- Где в коде: `articles/views.py`, `api/views.py`, `templates/articles/news_list.html`
- Как показать преподавателю:
  - В браузере фильтры/поиск на `/news/`, в API `GET /api/articles/?q=...&ordering=popular`.

### 4.7 Миграции + seed/fixtures
- Статус: ✅ выполнено
- Где в коде: `*/migrations/`, `core/management/commands/seed_demo.py`, `core/management/commands/bootstrap_all.py`
- Как показать преподавателю:
  - Команда `python manage.py bootstrap_all --seed`.

### 4.8 Валидация на уровне модели (`clean/validators`)
- Статус: ✅ выполнено
- Где в коде: `tournaments/models.py`, `interactions/models.py`
- Как показать преподавателю:
  - Открыть `Tournament.clean`, `MatchResult.clean`, `Subscription.clean`.

### 4.9 Статистика (`annotate/Count`)
- Статус: ✅ выполнено
- Где в коде: `api/views.py` (`teams_list`, `tournaments_list`), `articles/views.py` (агрегация реакций)
- Как показать преподавателю:
  - `GET /api/teams/` и `GET /api/tournaments/` (поля `players_count`, `matches_count`).

---

## 5. Шаблоны Django

### 5.1 Наследование base -> pages
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `templates/**/*.html`
- Как показать преподавателю:
  - Открыть страницу с `{% extends "base.html" %}`.

### 5.2 Переиспользуемые include-компоненты
- Статус: ✅ выполнено
- Где в коде: `templates/includes/*`
- Как показать преподавателю:
  - Открыть `templates/includes/news_card.html` и место include в `templates/articles/news_list.html`.

### 5.3 Циклы/условия/empty
- Статус: ✅ выполнено
- Где в коде: `templates/articles/news_list.html`, `templates/comments/comment_list_items.html`
- Как показать преподавателю:
  - Показать `{% for %}`, `{% if %}`, ветку пустого списка.

### 5.4 Каталог: список+пагинация+фильтры/поиск
- Статус: ✅ выполнено
- Где в коде: `templates/articles/news_list.html`, `articles/views.py`
- Как показать преподавателю:
  - На `/news/` показать фильтры, пагинацию, поиск.

### 5.5 Детальная страница сущности
- Статус: ✅ выполнено
- Где в коде: `templates/articles/news_detail.html`, `articles/views.py`
- Как показать преподавателю:
  - Открыть новость и показать автора/категории/обложку/действия по правам.

### 5.6 Личный кабинет с “моими” действиями
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `templates/accounts/profile.html`
- Как показать преподавателю:
  - Открыть `/accounts/profile/` и показать блок “Мои действия” (счётчики + последние избранные/комментарии).

### 5.7 Кастомный template filter/tag
- Статус: ✅ выполнено
- Где в коде: `articles/templatetags/news_media.py`, `teams/templatetags/team_media.py`, `dashboard/templatetags/user_groups.py`
- Как показать преподавателю:
  - Показать фильтр `news_image` и его использование в шаблоне.

### 5.8 Breadcrumbs / понятная навигация
- Статус: ✅ выполнено
- Где в коде: `templates/includes/breadcrumbs.html`, `core/views.py`, `articles/views.py`, `accounts/views.py`
- Как показать преподавателю:
  - Открыть любую внутреннюю страницу и показать breadcrumbs.

### 5.9 Безопасный вывод (без unsafe `safe`)
- Статус: ✅ выполнено
- Где в коде: `templates/**/*.html` (нет неоправданного `|safe`)
- Как показать преподавателю:
  - Показать рендер текста комментария/контента через стандартный escaping.

---

## 6. Админ-панель Django

### 6.1 Все модели зарегистрированы
- Статус: ✅ выполнено
- Где в коде: `accounts/admin.py`, `articles/admin.py`, `comments/admin.py`, `core/admin.py`, `interactions/admin.py`, `taxonomy/admin.py`, `teams/admin.py`, `tournaments/admin.py`
- Как показать преподавателю:
  - В `/admin/` показать списки разделов.

### 6.2 `list_display/search_fields/list_filter` >=5 моделей
- Статус: ✅ выполнено
- Где в коде: `articles/admin.py`, `teams/admin.py`, `tournaments/admin.py`, `comments/admin.py`, `taxonomy/admin.py`
- Как показать преподавателю:
  - Открыть 5 admin-классов и показать поля.

### 6.3 Inline редактирование
- Статус: ✅ выполнено
- Где в коде: `articles/admin.py` (`MediaAssetInline`)
- Как показать преподавателю:
  - В admin открыть Article и показать inline media.

### 6.4 `prepopulated_fields`/`readonly_fields`
- Статус: ✅ выполнено
- Где в коде: `articles/admin.py`, `teams/admin.py`, `tournaments/admin.py`, `taxonomy/admin.py`
- Как показать преподавателю:
  - В admin при создании статьи показать автозаполнение slug.

### 6.5 Ограничения прав в админке
- Статус: ✅ выполнено
- Где в коде: `accounts/management/commands/bootstrap_roles.py`, `dashboard/decorators.py`, `api/decorators.py`
- Как показать преподавателю:
  - Показать, что обычный user не входит в `/admin/`, а `bootstrap_roles` назначает permissions группе `Editors`.

### 6.6 Admin actions
- Статус: ✅ выполнено
- Где в коде: `articles/admin.py` (`action_publish`, `action_unpublish`)
- Как показать преподавателю:
  - Выбрать несколько статей и применить action.

### 6.7 `fieldsets` хотя бы 1 модель
- Статус: ✅ выполнено
- Где в коде: `articles/admin.py`
- Как показать преподавателю:
  - Открыть форму статьи в admin.

---

## 7. Статика и медиа

### 7.1 MEDIA_ROOT/MEDIA_URL + upload
- Статус: ✅ выполнено
- Где в коде: `kz_arena/settings.py`, `kz_arena/urls.py`, модели с `ImageField`
- Как показать преподавателю:
  - Загрузить cover статьи через dashboard.

### 7.2 Отображение изображений + placeholder
- Статус: ✅ выполнено
- Где в коде: `articles/templatetags/news_media.py`, `teams/templatetags/team_media.py`, `static/placeholders/news/*`
- Как показать преподавателю:
  - Открыть новость/команду без картинки и показать плейсхолдер.

### 7.3 Валидация файлов (тип/размер)
- Статус: ✅ выполнено
- Где в коде: `dashboard/forms.py`
- Как показать преподавателю:
  - Открыть `dashboard/forms.py` и показать `_validate_image_upload`, `clean_cover`, `clean_file`.

### 7.4 `collectstatic` настроен и описан
- Статус: ✅ выполнено
- Где в коде: `kz_arena/settings.py`, `README.md`
- Как показать преподавателю:
  - Показать `STATIC_ROOT` и команду `collectstatic --noinput` в README.

### 7.5 Favicon + webfonts/icons через static
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `static/img/favicon.svg`
- Как показать преподавателю:
  - Открыть `templates/base.html` (`<link rel="icon"...>`) и `static/img/favicon.svg`.

---

## 8. API (JSON)

### 8.1 5+ endpoint-ов
- Статус: ✅ выполнено
- Где в коде: `api/urls.py`, `api/views.py`
- Как показать преподавателю:
  - Показать маршруты: `/api/articles/`, `/api/articles/<slug>/`, `/api/teams/`, `/api/tournaments/`, `/api/search/`.

### 8.2 Фильтры API (>=5)
- Статус: ✅ выполнено
- Где в коде: `api/views.py` (`q`, `category`, `tag`, `kind`, `discipline`, `ordering`, `page`, `page_size`)
- Как показать преподавателю:
  - Пример: `/api/articles/?q=KZ&category=kibersport&ordering=popular&page=1&page_size=5`.

### 8.3 POST/PUT/DELETE только авторизованным (editor/staff)
- Статус: ✅ выполнено
- Где в коде: `api/views.py`, `api/decorators.py`
- Как показать преподавателю:
  - Без логина POST дает 403, под editor работает.

### 8.4 Единый формат ошибок
- Статус: ✅ выполнено
- Где в коде: `api/utils.py`, `api/views.py`
- Как показать преподавателю:
  - Невалидный payload на `POST /api/articles/` и показать JSON с `ok:false/error{code,message,details}`.

### 8.5 Мини-документация API в README
- Статус: ✅ выполнено
- Где в коде: `README.md` (раздел API + curl примеры)
- Как показать преподавателю:
  - Открыть раздел API в README.

---

## 9. Хостинг, домен, эксплуатация

Примечание: по вашему комментарию этот пункт для текущей проверки считается необязательным; ниже — фактический статус артефактов.

### 9.1 Домен и онлайн-доступ
- Статус: ⚠️ частично (локально готово, факт домена не подтвержден в репо)
- Где в коде: `README.md` содержит deploy-гайд, но нет реального домена
- Как показать преподавателю:
  - Показать готовность конфигов `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
- Минимальный план фикса:
  - После выдачи домена добавить URL в README и сделать smoke-ссылку.

### 9.2 HTTPS и HTTP->HTTPS
- Статус: ✅ выполнено (подготовка в коде и env; включается на хостинге)
- Где в коде: `kz_arena/settings.py` (`USE_HTTPS`, `SECURE_SSL_REDIRECT`)
- Как показать преподавателю:
  - Показать env-переменные в `settings.py`.

### 9.3 Регулярные обновления
- Статус: ✅ выполнено
- Где в коде: git history (серия коммитов)
- Как показать преподавателю:
  - `git log --oneline -n 15`.

### 9.4 PostgreSQL на проде
- Статус: ✅ выполнено (поддержка Postgres через env + fallback SQLite)
- Где в коде: `kz_arena/settings.py`, `.env.example`, `requirements.txt`, `README.md`
- Как показать преподавателю:
  - Открыть `DATABASES` в `settings.py`, `DB_*` в `.env.example`, инструкции в `README.md`.

### 9.5 Страница “О проекте” с авторами/ролями
- Статус: ✅ выполнено
- Где в коде: `templates/core/about.html`
- Как показать преподавателю:
  - Открыть `/about/` и показать секцию “Команда проекта”.

### 9.6 Мониторинг/логи/перезапуск в README
- Статус: ✅ выполнено
- Где в коде: `README.md`
- Как показать преподавателю:
  - Открыть в `README.md` раздел deploy с командами logs/status/restart.

### 9.7 Backup-стратегия
- Статус: ✅ выполнено
- Где в коде: `README.md`
- Как показать преподавателю:
  - Открыть в `README.md` блок backup-стратегии и пример `pg_dump`.

---

## 10. Дополнительные функции

### 10.1 Избранное
- Статус: ✅ выполнено
- Где в коде: `interactions/models.py`, `interactions/views.py`, `templates/articles/news_detail.html`, `static/js/main.js`
- Как показать преподавателю:
  - На детали новости нажать “Избранное” и показать изменение счетчика.

### 10.2 Отзывы/рейтинги 1-5 + средний рейтинг
- Статус: ✅ выполнено
- Где в коде: `interactions/models.py`, `interactions/views.py`, `interactions/urls.py`, `interactions/admin.py`, `articles/views.py`, `templates/articles/news_detail.html`, `interactions/migrations/0002_articlerating_and_more.py`
- Как показать преподавателю:
  - На `/news/<slug>/` поставить оценку 1–5 и показать средний рейтинг/количество; в VSCode показать модель и миграцию.

### 10.3 Автодополнение (AJAX) / live filter
- Статус: ✅ выполнено
- Где в коде: `articles/views.py` (`news_search`), `templates/articles/news_list.html`, `static/js/main.js` (`initAutocomplete`)
- Как показать преподавателю:
  - В поле поиска `/news/` ввести 2+ символа и показать dropdown.

### 10.4 Тёмная/светлая тема + localStorage
- Статус: ✅ выполнено
- Где в коде: `templates/base.html`, `templates/includes/navbar.html`, `static/js/main.js`, `static/css/style.css`
- Как показать преподавателю:
  - Переключить тему и перезагрузить страницу (состояние сохраняется).

### 10.5 Безопасность: rate limit login / captcha
- Статус: ✅ выполнено
- Где в коде: `accounts/views.py`, `kz_arena/settings.py` (`CACHES`)
- Как показать преподавателю:
  - Несколько раз ввести неверный пароль на `/accounts/login/` и показать сообщение о временной блокировке.

---

## Итоговая таблица (1..10)

| Раздел | Статус | Как показать (1 фраза) |
|---|---|---|
| 1 | ✅ | Открыть `settings/urls/base/README`, `pyproject.toml`, показать env/структуру и команды запуска. |
| 2 | ⚠️ | В браузере пройти `/`, `/news/` и интерактивы; в коде показать `style.css`/`main.js`. |
| 3 | ✅ | Продемонстрировать регистрацию/логин/профиль/роли и доступ к dashboard. |
| 4 | ✅ | Открыть модели + фильтры/поиск/API-статистику (`Count/annotate`). |
| 5 | ✅ | Показать шаблоны + breadcrumbs и блок “Мои действия” в `/accounts/profile/`. |
| 6 | ✅ | Показать admin-конфиги, inline/actions/fieldsets и `bootstrap_roles` с permissions для `Editors`. |
| 7 | ✅ | Продемонстрировать upload/placeholder и показать favicon + upload-validation в коде. |
| 8 | ✅ | Через `/api/...` показать endpoints, фильтры, защищенные методы и формат ошибок. |
| 9 | ⚠️* | Показать deploy-ready настройки, Postgres fallback, about/team, logs/backup docs; домен отложен (9.1). |
| 10 | ✅ | Показать избранное, автодополнение, theme toggle, рейтинги 1–5 и rate-limit логина. |

\* По вашему комментарию, раздел 9 сейчас необязательный для защиты до момента выдачи домена.

## Defense walkthrough (5–10 minutes)

1. Подготовка (30 сек):
   - Команды: `venv/bin/python manage.py check`, `venv/bin/python manage.py runserver`.
2. Архитектура (1 мин):
   - Показать `kz_arena/settings.py`, `kz_arena/urls.py`, список apps.
3. Публичная часть (1.5 мин):
   - `/` -> `/news/` (поиск, фильтры, пагинация) -> `/news/<slug>/`.
4. Аутентификация/роли (1 мин):
   - `login/register/profile`, показать `next=` и role-based доступ в navbar/dashboard.
5. Dashboard CRUD (1 мин):
   - Создать/изменить/опубликовать статью, проверить в `/news/`.
6. Интерактив (1 мин):
   - На detail: like/dislike/favorite/comments (AJAX).
7. API (1 мин):
   - `GET /api/articles/?ordering=popular&page=1&page_size=5`
   - `GET /api/search/?q=KZ`
   - Ошибка валидации для демонстрации формата error.
8. Admin (1 мин):
   - `ArticleAdmin`: `list_filter`, `actions`, `inline`.
9. Честно озвучить gap-ы (30 сек):
   - Шаблон-источник (п.2.1, отложено по согласованию) и домен/онлайн-доступ (п.9.1, ждете разрешение преподавателя).
