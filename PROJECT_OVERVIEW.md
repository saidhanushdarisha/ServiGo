# ServiGo — Project Presentation Notes

## One-line description
ServiGo is a Django-based home-services and EV-charging booking platform with role-based dashboards, secure authentication, booking lifecycle management, EV capacity/conflict protection, and customer reviews.

## Core modules
- Accounts: custom user model, customer/staff/admin roles, authentication and profiles.
- Services: categories, service catalogue, pricing, availability and service details.
- Bookings: service booking, staff assignment, status workflow and status history.
- EV Charging: station catalogue, search/filtering, time-slot booking and port-capacity protection.
- Dashboard: customer, staff and admin operational dashboards.
- Reviews: one review per completed service/EV booking, 1–5 rating, edit support and aggregate ratings.
- Core: home, contact, site settings and shared pages.

## Engineering enhancements
1. EV slot conflict prevention: overlapping bookings are checked against active reservations.
2. EV port capacity enforcement: a booking is accepted only when at least one port is available; the final check occurs inside a database transaction.
3. Customer statistics: profile totals are synchronized whenever service bookings are created, updated or deleted.
4. Booking timestamps: confirmed, started/active, completed and cancelled timestamps are recorded automatically from status transitions.
5. Reviews and ratings: completed bookings can receive a 1–5 rating and optional comment; duplicate reviews are prevented through one-to-one booking relationships.

## Local deployment
SQLite is retained for local development. Create `.env`, install `requirements.txt`, run migrations, seed demo data and start Django with `python manage.py runserver`.

## Railway deployment
When `DATABASE_URL` is present, settings automatically use PostgreSQL. Railway can provide this variable from its PostgreSQL service. The included `Procfile` runs migrations and starts Gunicorn. WhiteNoise serves collected static files.

## Presentation flow
Problem → Solution → Architecture → Key features → Engineering improvements → Deployment → Demo.
