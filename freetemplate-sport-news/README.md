# Sport News Template Pack

## 1) What is this template and why it exists

`template-sport-news/` is a standalone educational front-end template pack for a sports and esports news website.

It is designed for students who want to:
- practice semantic HTML/CSS/JS,
- build a dark modern news UI,
- later adapt the static layout to Django templates (`base.html`, `includes`, `static/`).

The template is intentionally framework-free (no React/Vue/Bootstrap JS, no bundlers).

## 2) How to open locally

Simple options:
- Double-click `index.html` in your file manager
- Open `template-sport-news/` with VS Code and use Live Server
- Or run a simple static server, for example:
  - `python -m http.server 8000` (inside `template-sport-news/`)

Then open `http://localhost:8000/`.

## 3) Folder structure

```text
template-sport-news/
  index.html
  catalog.html
  article.html
  teams.html
  tournaments.html
  matches.html
  about.html
  login.html
  register.html
  404.html
  500.html
  assets/
    css/
      style.css
      overrides.css
    js/
      main.js
    img/
      hero-main.svg
      card-sport.svg
      card-esport.svg
      team.svg
      tournament.svg
```

## 4) Included pages

- `index.html` - Homepage (hero, featured area, top of the day, tabs, CTA)
- `catalog.html` - News catalog (filters, grid, fake pagination)
- `article.html` - Article detail (toolbar, copy link, related news)
- `teams.html` - Team cards
- `tournaments.html` - Tournament cards
- `matches.html` - Match list + status filter
- `about.html` - About page + FAQ accordion
- `login.html` - Login form demo
- `register.html` - Register form demo + password strength
- `404.html` - Error page example
- `500.html` - Error page example

## 5) Implemented CSS effects (checklist-friendly)

1. Card hover lift (`.news-card:hover`)
2. Card image zoom on hover (`.news-card:hover img`)
3. Hero card hover lift
4. Brand mark rotate/scale on hover
5. Button hover/active transitions
6. Nav link hover background transition
7. Active nav item state styling
8. Dropdown open animation (opacity + translate)
9. Input/select focus ring and border transition
10. Chip hover + active state transition
11. Ticker item hover background/color change
12. Toast enter animation (`@keyframes toastIn`)
13. Skeleton shimmer animation (`@keyframes skeletonShimmer`)
14. Accordion chevron rotation + panel expand transition
15. Back-to-top reveal animation (opacity/translate)
16. Theme transition (colors/background changes via CSS variables)
17. Status pill color variants (live/upcoming/finished)
18. Footer link hover slide (`padding-left`)

## 6) Implemented JS scenarios (checklist-friendly)

1. Theme toggle (dark/light)
2. Theme persistence in `localStorage`
3. Sticky header state on scroll
4. Mobile burger menu open/close
5. Mobile dropdown toggle (submenu)
6. Breaking ticker auto-rotation
7. Breaking ticker prev/next controls
8. Generic modal open/close system
9. Search modal filtering results from page cards
10. Tabs switching (`data-tabs`)
11. Catalog text search filter
12. Catalog chip/category filter
13. Client-side sorting (newest/popular/oldest)
14. Fake pagination for visible cards
15. Filter persistence in `localStorage`
16. Match list status filter (all/live/upcoming/finished)
17. FAQ accordion open/close
18. Copy article link to clipboard (with fallback)
19. Expand/collapse article text
20. Password visibility toggle
21. Password strength meter (register)
22. Register form validation (password/confirm/terms)
23. Login form validation (demo)
24. Bookmark toggle on cards
25. Like button local counter toggle
26. Toast notifications
27. Dismissible alert box
28. Back-to-top button action
29. Skeleton demo show/hide button

## 7) How to adapt this template to Django (short guide)

### Step A: Create `base.html`
- Move shared `<head>`, header, footer, modal, toast, back-to-top into `base.html`
- Add blocks such as:
  - `{% block title %}`
  - `{% block content %}`
  - `{% block scripts %}`

### Step B: Move static files into Django `static/`
- Put CSS into `static/css/`
- Put JS into `static/js/`
- Put images into `static/img/`
- Replace links:
  - `assets/css/style.css` -> `{% static 'css/style.css' %}`
  - `assets/js/main.js` -> `{% static 'js/main.js' %}`

### Step C: Split repeated parts into includes
- Header -> `templates/includes/navbar.html`
- Footer -> `templates/includes/footer.html`
- Card markup -> `templates/includes/news_card.html`

### Step D: Replace static content with Django context
- Cards: loop through queryset/page object
- Headline/date/tags: map to model fields
- Links: replace `article.html` with `{% url ... %}` / `item.get_absolute_url`

### Step E: Replace fake JS features with backend logic when needed
- Fake catalog filters -> real GET query params
- Fake pagination -> Django `Paginator`
- Fake auth forms -> Django forms + CSRF + validation

## 8) Notes for students

- Start from working static HTML first.
- Keep `style.css` as the base design system.
- Put project-specific visual tweaks in `overrides.css`.
- Keep interactive features modular: each JS block should fail safely if markup is absent.
