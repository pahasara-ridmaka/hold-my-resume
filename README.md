<div align="center">

# 💼 HOLDMYRESUME

### _A streamlined Django platform to track, manage, and analyze your job search_

[![Django](https://img.shields.io/badge/Django-6.1-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![HTMX](https://img.shields.io/badge/HTMX-Fast%20UI-3366CC?logo=htmx)](https://htmx.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Local%20DB-003B57?logo=sqlite)](https://www.sqlite.org/)

🔗 **Live Demo:** [https://pridmaka.pythonanywhere.com](https://pridmaka.pythonanywhere.com)

---

</div>

🚀 **HOLDMYRESUME** organizes your job hunt in one centralized dashboard. Track application stages, store private resumes and cover letters, inspect visual metrics, and export analytics seamlessly.

## ✨ Core Features

- **Account Management:** User registration, authentication, profile editing, and password recovery
- **Application Tracking:** Link applications to companies/platforms with full stage workflows (`Applied`, `Interviewing`, `Offer`, `Rejected`)
- **Document Locker:** Private, secure storage for targeted resumes and cover letters
- **Dynamic UI:** Smooth slide-out drawer views powered by HTMX
- **Analytics & Export:** Visual dashboard breakdown with one-click CSV export
- **Admin Control:** Django admin panel integration for comprehensive data oversight

## 🧰 Tech Stack

- **Backend:** Python 3.12+, Django 6.1
- **Database:** SQLite (local development)
- **Frontend:** Django Templates, Custom CSS, HTMX
- **Storage:** Private local media directories

## 📦 Project Structure

```text
accounts/       Authentication and user profile workflows
applications/   Companies, applications, uploads, and status tracking
analytics/      Dashboard metrics and CSV export
config/         Django project settings and URL configuration
templates/      Shared core and legal templates
static/         CSS stylesheets, icons, and static assets
resumes/        Local storage for uploaded resumes
cover_letters/  Local storage for uploaded cover letters
```

## 🧪 Local Dev (Quick Start)

1. **Clone and create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies and migrate:**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install Django
   python manage.py migrate
   ```

3. **Create superuser and launch server:**
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

4. **Access the platform:**
   - App: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## 🛠️ Useful Commands

- `python manage.py check` — Inspect configuration for system issues
- `python manage.py test` — Run the test suite
- `python manage.py makemigrations` — Generate schema migrations
- `python manage.py migrate` — Apply database schema updates

## 🔐 Configuration & Security

- Development runs with `DEBUG = True` and local file storage.
- Set environment-specific secret keys, email backends, allowed hosts, and remote object storage (e.g., S3) prior to production deployment.

## ✅ Status

Active development. Demo live at [https://pridmaka.pythonanywhere.com](https://pridmaka.pythonanywhere.com).