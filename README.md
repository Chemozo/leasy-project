# Leasy Project

A Django-based platform for managing clients, vehicles, contracts, invoices, and reports.

---

## Requirements

- Python 3.8+
- Django 5.2+
- MySQL (for production, SQLite for development)

---

## Features

- **User Authentication**: Custom user model with email login.
- **Role-Based Access**: Sales, Operations, and Collections groups with permissions.
- **Clients**: Register, list, and search clients.
- **Vehicles**: Register, list, and manage vehicles, brands, and models.
- **Contracts**: Create and list contracts, enforce unique active contracts per client/vehicle.
- **Invoices**: Generate invoices via management command, track status (paid, pending, overdue).
- **Reports**: Upload data, generate Excel reports, and send them via email.
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

Deployment to [pythonanywhere.com](https://www.pythonanywhere.com/)

1. Go tu user dashboard
2. Navigate to consoles tab
3. Open a bash console
4. Follow instructions below:

   > https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/

5. From dashboard navigate to Databases
6. Create new database
7. Follow instructions to add environment variables:

   > https://help.pythonanywhere.com/pages/environment-variables-for-web-apps/

8. Edit a wsgi file:

```python
import os
import sys
from dotenv import load_dotenv

# Set your project folder path here
project_folder = os.path.expanduser('/home/<your-username>/leasy-project/core')
load_dotenv(os.path.join(project_folder, '.env'))

# Add the project root to the Python path
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

8. Go back to the bash console

```bash
# Run Migrations
./manage.py migrate

# Collect static files
./manage.py collectstatic
```

9.  Reload Your Web App

## Scheduled Tasks

To generate invoices automatically, add a scheduled task in PythonAnywhere:

```sh
cd /home/<username>/leasy-project/core && /home/<username>/.virtualenvs/<your-virtualenv>/bin/python manage.py generate_invoices
```

---

## Notes

- **Redis/async queue** for email/report will not be used in production due to limitations with PythonAnywhere.
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
