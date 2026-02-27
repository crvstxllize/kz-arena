# PROJECT STRUCTURE OVERVIEW (1 минута)
- Стек используется: Django (Python), HTML/CSS/JS, SQLite локально + поддержка PostgreSQL через env, JSON API без DRF.
- Точка входа:
  - `manage.py` — запуск команд Django.
  - `kz_arena/settings.py` — настройки проекта.
  - `kz_arena/urls.py` — корневые роуты и namespace include.
- Основные папки:
  - `/kz_arena` — глобальные настройки проекта (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py` если есть).
  - `/apps/...` — в этом проекте отдельной папки `apps/` нет; приложения лежат в корне: `accounts/`, `articles/`, `teams/`, `tournaments/`, `comments/`, `interactions/`, `taxonomy/`, `dashboard/`, `api/`, `core/`.
  - `/templates` — Django-шаблоны: `base.html`, страницы по приложениям (`templates/articles`, `templates/accounts`, `templates/core`, ...), компоненты в `templates/includes/`.
  - `/static` — фронтенд ассеты проекта: `static/css`, `static/js`, `static/img`, `static/placeholders`, `static/teams`.
  - `/media` — загруженные файлы (`media/logos` и др.).
  - `/api` — JSON API: `api/urls.py`, `api/views.py`, `api/utils.py`, `api/decorators.py`.
  - `/docs` — документы/вспомогательные материалы (например `docs/template-source/...`).
- Дополнительно для п.2.1:
  - `/freetemplate-sport-news` — отдельный учебный HTML/CSS/JS template pack (статические страницы + `assets/`).

---

## Пункт 1 — Основы и структура проекта

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `manage.py`
- `kz_arena/settings.py`
- `kz_arena/urls.py`
- `README.md`
- `.env.example`
- `pyproject.toml`
- `accounts/apps.py`, `api/apps.py`, `articles/apps.py`, `comments/apps.py`, `core/apps.py`, `dashboard/apps.py`, `interactions/apps.py`, `taxonomy/apps.py`, `teams/apps.py`, `tournaments/apps.py`
- `templates/base.html`
- `templates/includes/navbar.html`
- `templates/includes/footer.html`
- `templates/core/404.html`
- `templates/core/500.html`

### 2️⃣ Что именно показать в файле (конкретно)
- В `kz_arena/settings.py`: `DEBUG`, `ENV_NAME`, `SECRET_KEY`, `ALLOWED_HOSTS`, `TEMPLATES`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_ROOT`, `LOGGING`.
- В `kz_arena/urls.py`: `include(..., namespace=...)`, `handler404`, `handler500`.
- В `INSTALLED_APPS`: 10+ приложений и доменные app names.
- В `templates/base.html`: базовый layout + includes navbar/footer.
- В `pyproject.toml`: настройки `black` / `isort`.
- В `README.md`: quick start, миграции, superuser, collectstatic, deploy notes, тестовые логины.

### 3️⃣ Какие URL открыть в браузере
- `/`
- `/news/`
- `/teams/`
- Любой несуществующий URL для 404 (например `/no-such-page/`)

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- Это Django-проект с разделением на доменные приложения, все подключены через namespace в `kz_arena/urls.py`.
- Базовая структура вынесена в `templates/base.html`, а общие элементы навигации и футера — в includes.
- Настройки используют env-переменные, подготовлены static/media и прод-параметры, есть README с командами запуска и deploy-инструкциями.

---

## Пункт 2 — Дизайн + HTML + CSS + JS

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `templates/base.html`
- `templates/core/home.html`
- `templates/articles/news_list.html`
- `templates/articles/news_detail.html`
- `templates/includes/news_card.html`
- `templates/includes/navbar.html`
- `static/css/style.css`
- `static/js/main.js`
- `freetemplate-sport-news/`
- `freetemplate-sport-news/index.html`
- `freetemplate-sport-news/catalog.html`
- `freetemplate-sport-news/article.html`
- `freetemplate-sport-news/login.html`
- `freetemplate-sport-news/README.md`
- `freetemplate-sport-news/assets/css/style.css`
- `freetemplate-sport-news/assets/js/main.js`

### 2️⃣ Что именно показать в файле (конкретно)
- В `templates/base.html`: семантика `header/main/footer`, подключение CSS/JS через `{% static %}`.
- В `templates/core/home.html` и `templates/articles/news_list.html`: секции “Главное”, “Топ дня”, сетка карточек.
- В `static/css/style.css`: CSS variables (`:root`), брейкпоинты `@media`, `:focus-visible`, hover/transition эффекты.
- В `static/js/main.js`: инициализацию интерактивов (theme toggle, autocomplete, filters, comments/interactions и т.д.).
- В `freetemplate-sport-news/README.md`: список реализованных CSS эффектов и JS сценариев, структура template pack.

### 3️⃣ Какие URL открыть в браузере
- `/`
- `/news/`
- `/news/<slug>/` (любая существующая новость)
- `/accounts/login/`
- `/accounts/register/`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- В основном проекте UI уже реализован: темная тема, карточки, фильтры, формы, адаптивность и интерактив на `static/css/style.css` и `static/js/main.js`.
- Дополнительно я подготовил отдельный учебный template pack `freetemplate-sport-news/` как изолированный HTML/CSS/JS шаблон для студентов, не ломая Django-проект.
- Там есть отдельные страницы, список эффектов и сценариев, а также инструкция, как переносить шаблон в Django.

---

## Пункт 3 — Пользователи, роли и формы

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `accounts/urls.py`
- `accounts/views.py`
- `accounts/forms.py`
- `templates/accounts/register.html`
- `templates/accounts/login.html`
- `templates/accounts/profile.html`
- `templates/accounts/profile_edit.html`
- `templates/accounts/password_change.html`
- `templates/accounts/password_reset_stub.html`
- `dashboard/decorators.py`
- `api/decorators.py`
- `core/management/commands/seed_demo.py`
- `dashboard/forms.py`
- `dashboard/views.py`

### 2️⃣ Что именно показать в файле (конкретно)
- В `accounts/urls.py`: реальные роуты `/accounts/register/`, `/accounts/login/`, `/accounts/profile/`, `/accounts/profile/edit/`.
- В `accounts/views.py`: логика `next=`, messages framework, профиль/редактирование, смена пароля/заглушка reset.
- В `accounts/forms.py`: валидация регистрации и `clean_email` (защита от дублей).
- В `dashboard/decorators.py` и `api/decorators.py`: role-based access (user/editor/staff).
- В `dashboard/forms.py`: ModelForm/CRUD формы для статей.

### 3️⃣ Какие URL открыть в браузере
- `/accounts/register/`
- `/accounts/login/?next=/dashboard/`
- `/accounts/profile/`
- `/accounts/profile/edit/`
- `/accounts/password-change/`
- `/accounts/password-reset/`
- `/dashboard/`
- `/dashboard/articles/`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- В проекте есть полноценный auth-flow: регистрация, логин/логаут, профиль, редактирование профиля и смена пароля.
- Права разделены минимум на роли user/editor/staff: обычный пользователь не получает доступ к dashboard/API write methods.
- Формы сделаны на Django Forms/ModelForms, с валидацией и понятными сообщениями об ошибках.

---

## Пункт 4 — ORM, модели и связи

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `articles/models.py`
- `teams/models.py`
- `tournaments/models.py`
- `interactions/models.py`
- `accounts/models.py`
- `taxonomy/models.py`
- `comments/models.py`
- `core/models.py`
- `articles/views.py`
- `api/views.py`
- `core/utils.py`
- `core/management/commands/bootstrap_all.py`
- `core/management/commands/seed_demo.py`
- Любая папка `*/migrations/` (например `articles/migrations/`, `interactions/migrations/`)

### 2️⃣ Что именно показать в файле (конкретно)
- В моделях: примеры `ForeignKey`, `ManyToMany`, `OneToOne` (например `Article.categories`, `Match.tournament`, `MatchResult.match`).
- `slug` и уникальность slug в доменных моделях (`articles`, `teams`, `tournaments`, `taxonomy`).
- `Meta.ordering`, `indexes` и модельные валидаторы / `clean()` (`Tournament.clean`, `MatchResult.clean`, `Subscription.clean`).
- В `articles/views.py` / `api/views.py`: `select_related`, `prefetch_related`, фильтрация/поиск/сортировка, `annotate`/`Count`.
- В `bootstrap_all.py`/`seed_demo.py`: подготовка тестовых данных.

### 3️⃣ Какие URL открыть в браузере
- `/news/`
- `/news/<slug>/`
- `/teams/`
- `/tournaments/`
- `/matches/`
- `/api/teams/`
- `/api/tournaments/`
- `/api/articles/?q=KZ&ordering=popular`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- Модельный слой покрывает домен спорта/киберспорта: новости, команды, турниры, матчи, комментарии, реакции, избранное, категории и теги.
- Связи реализованы через FK/M2M/O2O, URL — человекочитаемые по slug.
- В выборках использованы ORM-оптимизации (`select_related/prefetch_related`) и API-статистика через `annotate/Count`.

---

## Пункт 5 — Шаблоны Django

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `templates/base.html`
- `templates/includes/` (папка)
- `templates/includes/news_card.html`
- `templates/includes/breadcrumbs.html`
- `templates/articles/news_list.html`
- `templates/articles/news_detail.html`
- `templates/comments/comment_list_items.html`
- `templates/accounts/profile.html`
- `accounts/views.py`
- `articles/views.py`
- `articles/templatetags/news_media.py`
- `teams/templatetags/team_media.py`
- `dashboard/templatetags/user_groups.py`

### 2️⃣ Что именно показать в файле (конкретно)
- Наследование шаблонов: `{% extends "base.html" %}` и блоки в страницах.
- Include-компоненты: `news_card`, `breadcrumbs`, navbar/footer.
- Циклы/условия/ветка пустого списка (`for`, `if`, `empty`).
- В `templates/articles/news_list.html`: поиск, фильтры, пагинация и сохранение querystring.
- В `templates/accounts/profile.html` + `accounts/views.py`: блок “Мои действия”.
- Кастомные template tags/filters: `news_image`, `team_media`, `has_group`.

### 3️⃣ Какие URL открыть в браузере
- `/news/`
- `/news/<slug>/`
- `/accounts/profile/`
- `/teams/`
- `/tournaments/`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- Все страницы наследуются от `base.html`, а повторяющиеся части вынесены в include-компоненты.
- В шаблонах есть циклы, условия, breadcrumbs, фильтры/пагинация и безопасный вывод данных без необоснованного `safe`.
- Для медиа и ролей используются кастомные template tags/filters.

---

## Пункт 6 — Админ-панель Django

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `articles/admin.py`
- `teams/admin.py`
- `tournaments/admin.py`
- `comments/admin.py`
- `taxonomy/admin.py`
- `interactions/admin.py`
- `accounts/admin.py`
- `core/admin.py`
- `accounts/management/commands/bootstrap_roles.py`
- `dashboard/decorators.py`
- `api/decorators.py`

### 2️⃣ Что именно показать в файле (конкретно)
- Регистрацию моделей в admin-модулях.
- `list_display`, `search_fields`, `list_filter` минимум в 5 admin-классах.
- Inline-пример: `MediaAssetInline` в `articles/admin.py`.
- `prepopulated_fields` и/или `readonly_fields` в админке.
- `action_publish`, `action_unpublish` (admin actions).
- `fieldsets` в `ArticleAdmin`.
- В `bootstrap_roles.py`: назначение permissions группе `Editors`.

### 3️⃣ Какие URL открыть в браузере
- `/admin/`
- `/admin/articles/article/` (или раздел статей в админке)

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- Админка настроена не только “по умолчанию”: есть фильтры, поиск, action-ы, fieldsets и inline-редактирование.
- Права разделены: обычный пользователь не должен попасть в admin, а группа `Editors` получает нужные разрешения через bootstrap-команду.
- Это позволяет использовать админку как рабочий инструмент управления контентом.

---

## Пункт 7 — Статика и медиа

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `kz_arena/settings.py`
- `kz_arena/urls.py`
- `dashboard/forms.py`
- `articles/templatetags/news_media.py`
- `teams/templatetags/team_media.py`
- `static/placeholders/news/` (папка)
- `static/img/favicon.svg`
- `templates/base.html`
- `README.md`
- `media/` (папка, если уже есть загруженные файлы)

### 2️⃣ Что именно показать в файле (конкретно)
- В `settings.py`: `MEDIA_URL`, `MEDIA_ROOT`, `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`.
- В `kz_arena/urls.py`: `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` для DEBUG.
- В `dashboard/forms.py`: `_validate_image_upload`, `clean_cover`, `clean_file` (тип/размер).
- В templatetags: fallback на placeholder, если изображения нет.
- В `templates/base.html`: подключение favicon через `{% static %}`.
- В `README.md`: `collectstatic --noinput` и замечания по прод-сборке статики.

### 3️⃣ Какие URL открыть в браузере
- `/news/`
- `/news/<slug>/`
- `/teams/`
- `/teams/<slug>/`
- `/dashboard/articles/create/` (для показа upload-формы, если есть доступ)

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- В проекте настроены и static, и media: загрузка файлов работает через dashboard, а отображение в шаблонах безопасно обрабатывает отсутствие картинок.
- Есть плейсхолдеры для новостей/команд и валидация загружаемых изображений по типу и размеру.
- Для прод-развертывания команда `collectstatic` и настройки статики описаны в README.

---

## Пункт 8 — API (JSON)

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `api/urls.py`
- `api/views.py`
- `api/utils.py`
- `api/decorators.py`
- `README.md`

### 2️⃣ Что именно показать в файле (конкретно)
- В `api/urls.py`: 5+ endpoint-ов (`articles`, `teams`, `tournaments`, `search`, root).
- В `api/views.py`: фильтры (`q`, `category`, `tag`, `kind`, `discipline`, `ordering`, `page`, `page_size`).
- В `api/decorators.py`: защита write-методов (editor/staff only).
- В `api/utils.py`: единый формат ошибок `ok:false/error{code,message,details}`.
- В `README.md`: мини-документация API и примеры запросов.

### 3️⃣ Какие URL открыть в браузере
- `/api/`
- `/api/articles/`
- `/api/articles/?q=KZ&ordering=popular&page=1&page_size=5`
- `/api/articles/<slug>/` (или `/api/articles/<id>/`)
- `/api/teams/`
- `/api/tournaments/`
- `/api/search/?q=KZ`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- API покрывает основные сущности проекта и умеет фильтрацию, сортировку и пагинацию через query-параметры.
- Read/write доступ разделён: модификация данных доступна только авторизованным editor/staff.
- Ошибки возвращаются в одном JSON-формате, а README содержит примеры для быстрого тестирования.

---

## Пункт 9 — Хостинг, домен, эксплуатация

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `kz_arena/settings.py`
- `.env.example`
- `requirements.txt`
- `README.md`
- `templates/core/about.html`

### 2️⃣ Что именно показать в файле (конкретно)
- В `settings.py`: `USE_HTTPS`, `SECURE_SSL_REDIRECT`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASES` с Postgres fallback.
- В `.env.example`: `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- В `requirements.txt`: драйвер PostgreSQL (`psycopg[binary]`).
- В `README.md`: deploy steps, restart/logs/status, backup strategy (`pg_dump`).
- В `templates/core/about.html`: секция про команду/роли участников.

### 3️⃣ Какие URL открыть в браузере
- `/about/`
- (Если домен уже выдан позже) ваш прод-URL проекта

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- По эксплуатации проект подготовлен: есть env-настройки для прод-режима, HTTPS-переключатели, Postgres-конфиг и инструкции по логам/перезапуску/backup в README.
- Отдельно показана страница “О проекте” с командной подачей.
- Пункт с реальным доменом (`9.1`) зависит от выдачи домена преподавателем, поэтому сейчас показываю готовность конфигов и документации.

---

## Пункт 10 — Дополнительные функции

### 1️⃣ Что открыть в Explorer (конкретные пути)
- `interactions/models.py`
- `interactions/views.py`
- `interactions/urls.py`
- `interactions/admin.py`
- `interactions/migrations/0002_articlerating_and_more.py`
- `articles/views.py`
- `templates/articles/news_detail.html`
- `templates/articles/news_list.html`
- `accounts/views.py`
- `kz_arena/settings.py` (блок `CACHES`)
- `static/js/main.js`
- `static/css/style.css`

### 2️⃣ Что именно показать в файле (конкретно)
- В `interactions/models.py`: избранное, рейтинг 1–5 и `UniqueConstraint` (1 рейтинг на пользователя/объект).
- В миграции `0002_...`: создание таблицы рейтингов.
- В `articles/views.py`: агрегация среднего рейтинга и количества оценок.
- В `templates/articles/news_detail.html`: UI избранного/рейтинга/интерактивов.
- В `articles/views.py` + `templates/articles/news_list.html` + `static/js/main.js`: автодополнение поиска.
- В `templates/base.html` / `templates/includes/navbar.html` / `static/js/main.js`: переключатель темы + localStorage.
- В `accounts/views.py` + `kz_arena/settings.py`: login rate limit через cache.

### 3️⃣ Какие URL открыть в браузере
- `/news/`
- `/news/<slug>/`
- `/accounts/login/`
- `/accounts/profile/`
- (опционально) `/api/search/?q=...`

### 4️⃣ Что сказать преподавателю (2–4 предложения)
- В проекте есть реальные дополнительные функции: избранное, рейтинги 1–5 со средним значением, автодополнение поиска и переключение темы с сохранением в localStorage.
- Для безопасности добавлен простой rate-limit логина на основе cache.
- Эти функции показаны на живых страницах и подтверждаются кодом в `interactions/*`, `articles/views.py`, `accounts/views.py` и `static/js/main.js`.

# 10-МИНУТНЫЙ СЦЕНАРИЙ ЗАЩИТЫ (тайминг)

00:00–01:00 → Пункт 1 (структура/стек): `manage.py`, `kz_arena/settings.py`, `kz_arena/urls.py`, `INSTALLED_APPS`, `base.html`, README.
01:00–02:00 → Пункт 2 (UI/HTML/CSS/JS): `/`, `/news/`, `static/css/style.css`, `static/js/main.js`, папка `freetemplate-sport-news/` + ее `README.md`.
02:00–03:00 → Пункт 3 (auth/roles/forms): `/accounts/register/`, `/accounts/login/?next=/dashboard/`, `/accounts/profile/`, `accounts/views.py`, `accounts/forms.py`, `dashboard/decorators.py`.
03:00–04:00 → Пункт 4 (ORM/models): `articles/models.py`, `tournaments/models.py`, `interactions/models.py`, `articles/views.py` (`select_related/prefetch_related`), `/api/teams/`.
04:00–05:00 → Пункт 5 (templates): `templates/base.html`, `templates/includes/news_card.html`, `templates/articles/news_list.html`, `/news/`, `/accounts/profile/`.
05:00–06:00 → Пункт 6 (admin): `/admin/`, `articles/admin.py` (actions/inline/fieldsets), `bootstrap_roles.py`.
06:00–07:00 → Пункт 7 (static/media): `kz_arena/settings.py`, `dashboard/forms.py` (upload validation), `templates/base.html` (favicon), показать страницу с placeholder.
07:00–08:00 → Пункт 8 (API): `/api/`, `/api/articles/?q=KZ&ordering=popular&page=1&page_size=5`, `/api/search/?q=KZ`, `api/utils.py` (error format).
08:00–09:00 → Пункт 9 (deploy readiness): `kz_arena/settings.py` (HTTPS/ALLOWED_HOSTS/DATABASES), `.env.example`, `requirements.txt`, `README.md`, `/about/`.
09:00–10:00 → Пункт 10 + вывод: `/news/<slug>/` (избранное/рейтинг), `/news/` (автодополнение), `/accounts/login/` (rate limit), кратко проговорить, что 9.1 закрывается после выдачи домена.
