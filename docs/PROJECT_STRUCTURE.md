# Project Structure

```text
ServiGo/
├── config/                  # Django project configuration
├── accounts/                # Authentication & user profiles
├── services/                # Home-service catalogue
├── bookings/                # Service booking workflow
├── ev_charging/             # EV stations & charging bookings
├── reviews/                 # Ratings & reviews
├── dashboard/               # Role-based dashboards
├── core/                    # Public pages, settings, seed command
├── templates/               # Feature-based Django templates
├── static/                  # CSS, JS and images
├── media/                   # Runtime uploaded media (ignored)
├── staticfiles/             # Collected production static files (ignored)
├── tests/                   # Automated tests by feature
├── scripts/                 # Deployment/maintenance helpers
├── docs/                    # Engineering documentation
├── screenshots/             # Project screenshots
├── images/                  # Source/demo image assets
├── manage.py                # Django CLI entrypoint
├── requirements.txt         # Python dependencies
├── build.sh                 # Railway/production build command
├── railway-start.sh         # Railway start command
├── railway.json             # Railway deployment configuration
├── .env.example             # Safe environment template
└── README.md                # Developer and deployment guide
```

The Django applications remain at the repository root intentionally: this is the standard Django convention and keeps imports, migrations and deployment simple.
