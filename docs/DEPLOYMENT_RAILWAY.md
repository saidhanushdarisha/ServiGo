# Railway Deployment

1. Push the project to GitHub. Never commit `.env`, credentials or `db.sqlite3`.
2. Create a Railway project and add a PostgreSQL service.
3. Deploy the repository as the Django application.
4. Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` as environment variables.
5. Railway provides `DATABASE_URL`; ServiGo automatically uses PostgreSQL when it exists.
6. Build command: `./build.sh`.
7. Start command: `./railway-start.sh` or `gunicorn config.wsgi:application`.
8. After first deployment, create an admin with `python manage.py createsuperuser` from the Railway shell.
