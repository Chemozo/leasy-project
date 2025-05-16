# Leasy Project

A Django-based platform for managing clients, vehicles, contracts, invoices, and reports.

---

## Features

- **User Authentication**: Custom user model with email login.
- **Role-Based Access**: Sales, Operations, and Collections groups with permissions.
- **Clients**: Register, list, and search clients.
- **Vehicles**: Register, list, and manage vehicles, brands, and models.
- **Contracts**: Create and list contracts, enforce unique active contracts per client/vehicle.
- **Invoices**: Generate invoices via management command, track status (paid, pending, overdue).
- **Reports**: Upload data, generate Excel reports, and send them via email.
- **Admin Panel**: Manage all entities via Django admin.
- **File Uploads**: Supports .xlsx and .csv files for bulk data import.
- **Responsive UI**: Bootstrap-based templates.

---

## Setup

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd leasy-project/core
```

### 2. Create and activate a virtual environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```sh
pip install -r ../requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in `core/` with:

```
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
```

For production, also add:

```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
```

### 5. Run migrations

```sh
python manage.py migrate
```

### 6. Create a superuser

```sh
python manage.py createsuperuser
```

### 7. Collect static files (for production)

```sh
python manage.py collectstatic
```

### 8. Run the development server

```sh
python manage.py runserver
```

---

## Deployment (PythonAnywhere)

- Update `ALLOWED_HOSTS` in `core/settings.py` to include your PythonAnywhere domain.
- Set up your MySQL database and environment variables in the PythonAnywhere dashboard.
- Map `/static/` to `/home/<username>/leasy-project/core/staticfiles` in the Web tab.
- Reload your web app after each change.

---

## Scheduled Tasks

To generate invoices automatically, add a scheduled task in PythonAnywhere:

```sh
cd /home/<username>/leasy-project/core && /home/<username>/.virtualenvs/<your-virtualenv>/bin/python manage.py generate_invoices
```

---

## Notes

- **No Redis/async queue is required** for email/report tasks; they run synchronously.
- For background tasks or async processing, see the comments in the code and this README.
- All sensitive settings should be managed via environment variables.

---

## Technical Test Requirements

- [x] Custom user model with email login
- [x] Role-based permissions (Sales, Operations, Collections)
- [x] CRUD for clients, vehicles, contracts
- [x] Invoice generation and status tracking
- [x] File upload and bulk import
- [x] Report generation and email delivery
- [x] Responsive Bootstrap UI
- [x] Admin panel for all models

---

## License

MIT License

---
