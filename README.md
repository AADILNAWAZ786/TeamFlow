# TeamFlow — Smart Leave & Task Handover

TeamFlow is a Django-based HR workflow prototype that connects employee leave requests with unfinished tasks and handover responsibilities. Its goal is to make coverage gaps visible before leave is approved.

## Features

- **Authentication:** Django login, logout, and employee registration.
- **Role-based access:** Employee and Manager roles implemented with Django Groups. Server-side checks protect manager views and approval actions.
- **Leave requests:** Employees submit leave dates, leave type, and a reason. Managers review pending requests.
- **Task tracking:** Employees create tasks with descriptions, due dates, and priorities.
- **Task handover:** Employees connect a task to a leave request, assign an active backup colleague, and add handover notes. The assigned backup can accept or decline.
- **Handover readiness:** The app checks relevant unfinished tasks and blocks manager approval when required handovers are missing or not accepted.
- **Manager overview:** Team profiles, leave requests, upcoming absences, and outstanding handovers.
- **Local AI helpers:** Optional Ollama integration for drafting handover instructions, explaining handover risks, and answering questions about accessible app records. The local model does not make approval decisions.

## Technology

- Python and Django
- SQLite for the local prototype
- Django templates, HTML/CSS, and Bootstrap 5
- Django built-in authentication and Groups
- Ollama with `llama3.2:1b` for local AI inference

## Database overview

The application uses Django's built-in user and group tables, plus these app models:

- `EmployeeProfile` — HR-specific details linked one-to-one with a user
- `LeaveRequest` — dates, leave type, reason, status, and reviewer
- `Task` — owner, description, deadline, priority, and status
- `Handover` — leave request, task, backup employee, notes, and acceptance status

Django migrations are committed under `core/migrations/` and should not be removed from version control.

## Requirements

- Python 3.12 or later compatible with your chosen Django version
- Git
- Optional: Ollama and the `llama3.2:1b` model for local AI features
- Internet access for installing packages and loading Bootstrap from its CDN

## Run locally on Windows PowerShell

Open PowerShell in the project directory (the folder containing `manage.py`).

```powershell
# Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set a Django secret key in your Windows user environment (one-time setup)
$key = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
[Environment]::SetEnvironmentVariable("DJANGO_SECRET_KEY", $key, "User")
$env:DJANGO_SECRET_KEY = $key

# IMPORTANT: in config/settings.py, add `import os` near the imports
# and replace Django's generated SECRET_KEY literal with:
# SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
# Do not commit the generated secret key to Git.

# Create/update the local database
python manage.py migrate

# Create an administrator account
python manage.py createsuperuser

# Start Django's development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. Django Admin is at <http://127.0.0.1:8000/admin/>.

New registrations are assigned the Employee group by the application. To grant Manager access, sign in to Django Admin with a superuser, open **Groups**, ensure the `Manager` group exists, and add the appropriate user to it. Do not grant superuser status to ordinary managers or employees.

## Enable local AI with Ollama (optional)

1. Install Ollama for Windows from <https://ollama.com/download/windows>.
2. Open a new terminal and download the model:

   ```powershell
   ollama pull llama3.2:1b
   ```

3. Verify it is installed:

   ```powershell
   ollama list
   ```

4. Ensure the Ollama local service is running. TeamFlow calls its local generation endpoint at `http://127.0.0.1:11434/api/generate`.
5. Use the **Generate AI Draft**, **Explain Risk**, and **Ask TeamFlow** features in the app.

The local AI path does not require an OpenAI API key and does not make paid OpenAI API calls. Model downloads use internet bandwidth and disk space. The quality and speed of responses depend on the machine and model. AI output can be incorrect: review generated notes and verify operational facts. Leave approval and authorization must remain controlled by Django's server-side rules, not by AI output.

## Security and project status

This is a buildathon/development prototype, not a production-ready HR system.

- Do not commit API keys, passwords, `.env` files, the local SQLite database, or your virtual environment.
- The OpenAI API key is not needed for the local Ollama setup. Never put secret keys in templates or frontend JavaScript.
- Use Django's server-side permission checks for every protected action.
- Use a production-grade deployment configuration before exposing this application publicly: set `DEBUG = False`, configure `ALLOWED_HOSTS`, use HTTPS, review CSRF/session settings, and consider PostgreSQL for deployment.
- Before production, review account deletion/retention rules, data privacy, audit logging, input validation, concurrency, and error handling.
- Some dashboard data or demo seed data may be intended for local testing. Do not use shared demo passwords for real accounts.

## Useful commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## License

No license has been specified yet. Add a `LICENSE` file before distributing the project if you want to grant others explicit reuse permissions.
