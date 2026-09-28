# ServiGo Architecture

## Application layers

- `config/` — Django project configuration, URLs, ASGI/WSGI entrypoints.
- `accounts/` — custom user model, authentication, profiles and account flows.
- `services/` — service catalogue and service discovery.
- `bookings/` — home-service booking lifecycle, assignments and status history.
- `ev_charging/` — EV station discovery, charging bookings, capacity and conflict rules.
- `reviews/` — completed-booking ratings and written reviews.
- `dashboard/` — customer, staff and admin operational dashboards.
- `core/` — public pages, site settings, shared context and seed data.
- `templates/` — presentation layer grouped by feature.
- `static/` — CSS, JavaScript and application images.
- `tests/` — feature-focused automated tests.
- `scripts/` — operational/deployment helper scripts.
- `docs/` — architecture and deployment documentation.

## Data flow

Browser → URL router → View/Form → Service/Business Rule → Django ORM → SQLite/PostgreSQL.

The project uses SQLite when `DATABASE_URL` is absent and PostgreSQL when `DATABASE_URL` is provided.
