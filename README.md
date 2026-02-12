# KZ Arena

Basic Django foundation for KZ Arena with shared templates/static structure and placeholder pages.

## Setup

1. Create and activate a virtual environment.

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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create env file from example:
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start development server:
```bash
python manage.py runserver
```

## Environment variables

`.env.example` contains:
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS` (comma-separated)
