# Repository Guidelines

## Project Structure & Module Organization

This repository is a Django project named `registre_objets`.

- `manage.py` is the entry point for administrative commands.
- `registre_objets/` contains settings and the root URL, ASGI, and WSGI configuration.
- `objets_trouves/` contains the application models, forms, views, URL routes, migrations, templates, and tests.
- `theme/` contains the Django Tailwind app, templates, static assets, and source CSS under `theme/static_src/src/`.
- `staticfiles/` is the collected static output; `db.sqlite3` is the local development database.

Keep business logic in the `objets_trouves` app, add schema changes through migrations, and keep generated static output out of source edits.

## Build, Test, and Development Commands

Activate the included environment before running Python commands:

```bash
source env/bin/activate
python manage.py migrate                 # Apply database migrations
python manage.py runserver               # Start the development server
python manage.py test                    # Run Django tests
python manage.py collectstatic           # Collect static files when needed
```

Build or watch Tailwind assets from `theme/static_src`:

```bash
npm install                               # Install frontend dependencies
npm run dev                               # Watch and rebuild CSS
npm run build                             # Create minified production CSS
```

## Coding Style & Naming Conventions

Use four spaces for Python indentation and follow PEP 8. Name Python modules and functions in `snake_case`, classes in `PascalCase`, and Django URL names in lowercase `snake_case`. Keep templates in app-specific directories such as `objets_trouves/templates/objets_trouves/`. Match the existing French domain terminology when extending models, forms, or user-facing validation messages.

## Testing Guidelines

Tests use Django’s built-in `TestCase` and live in `objets_trouves/tests.py` (or additional `test_*.py` modules in that app). Name test classes `Test...` and methods `test_...`. Run the full suite with `python manage.py test`; add coverage for model validation, form cleaning, views, and endpoint behavior when changing those areas.

## Commit & Pull Request Guidelines

No usable commit history is included in this checkout. Use short, imperative commit subjects such as `Add object search validation`, keeping unrelated changes separate. Pull requests should explain the behavior change, identify migrations or configuration updates, include test commands and results, and attach screenshots for template or styling changes. Call out any required environment variables or data migration steps.

## Security & Configuration Tips

Do not commit production secrets, database files, or debug settings. Move `SECRET_KEY`, `DEBUG`, and allowed hosts to environment-specific configuration before deployment, and review CSRF and API permissions when adding endpoints.
