# HOLDMYRESUME - Job Application Tracker

> Development project

A Django application for organizing job applications, tracking their progress, and reviewing application analytics. Users can create an account, manage their profile, attach resumes and cover letters, update application statuses, and export analytics as CSV.

## Current Features

- User registration, login, logout, password reset, profile editing, and password changes
- Application records linked to a company and optional application platform
- Application statuses: Applied, Interviewing, Offer, and Rejected
- Optional job URLs, descriptions, application dates, resumes, and cover letters
- Analytics dashboard with CSV export
- Private local storage for uploaded resumes and cover letters
- Django admin interface

## Technology

- Python
- Django 6.1
- SQLite for local development
- Django templates, CSS, and HTMX-based drawer interactions

## Development Setup

### Prerequisites

- Python 3.12 or newer
- `pip`

### Installation

From the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install Django
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Apply database migrations:

```bash
python manage.py migrate
```

Create an administrator account when needed:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. The admin interface is available at <http://127.0.0.1:8000/admin/>.

## Useful Commands

```bash
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
```

## Project Structure

```text
accounts/       Authentication and user profile workflows
applications/   Companies, applications, uploads, and status tracking
analytics/      Dashboard metrics and CSV export
config/         Django project settings and URL configuration
templates/      Shared and legal templates
static/         CSS and image assets
resumes/        Local resume upload storage
cover_letters/  Local cover-letter upload storage
```

## Development Notes

- The default database is `db.sqlite3`.
- Uploaded files are stored locally in `resumes/` and `cover_letters/` during development.
- The current settings use `DEBUG = True` and development credentials. Configure environment-specific secrets, email, hosts, and file storage before deployment.
- No dependency lockfile or requirements file is currently included; dependencies should be recorded as the project moves toward deployment.
