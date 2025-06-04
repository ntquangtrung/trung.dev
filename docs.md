# Django By Example - Shop Project

## 1. Basic Setup

1. Run:

   ```bash
   pyenv local 3.13
   ```

2. Run:

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

   _(Run `deactivate` to deactivate the virtual environment.)_

4. _(Optional)_ Install all dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   _(Use this if you already have a `requirements.txt` file.)_

5. _(Optional)_ Save installed packages to `requirements.txt`:

   ```bash
   pip freeze > requirements.txt
   ```

6. _(Optional)_ Uninstall all packages listed in `requirements.txt`:
   ```bash
   pip uninstall -r requirements.txt -y
   ```

---

## 2. Initialize Project

1. Create a new Django project:

   ```bash
   django-admin startproject <project-name> .
   ```

2. Navigate to the project directory:

   ```bash
   cd <project-name>
   ```

3. Run the development server:

   ```bash
   python3 manage.py runserver --settings=config.settings.development
   ```

4. _(Optional)_ Create a new app:

   ```bash
   python3 manage.py startapp <app_name>
   ```

5. Create a superuser:

   ```bash
   python3 manage.py createsuperuser
   ```

6. Open the Django interactive shell:

   ```bash
   python3 manage.py shell
   ```

   _(Type `exit()` or `quit()` to close the shell.)_

7. Collect static files for production:

   ```bash
   python3 manage.py collectstatic --settings=config.settings.production
   ```

8. _(Optional)_ Run the server with SSL:
   ```bash
   python3 manage.py runserver_plus --cert-file cert.crt
   ```

---

## 3. Migrations with Development Settings

1. _(Optional)_ View the SQL for a migration:

   ```bash
   python3 manage.py sqlmigrate <app_name> <migration_id>
   ```

2. _(Optional)_ Generate a migration file:

   ```bash
   python3 manage.py makemigrations <app_name> --settings=config.settings.development
   ```

3. Apply migrations:
   ```bash
   python3 manage.py migrate <app_name|optional> --settings=config.settings.development
   ```

---

## Superuser Credentials

- **Username:** `root`
- **Email:** `ng.qtrung95@gmail.com`
- **Password:** `123456`

---

## Test Credentials

- **Password:** `Apassword@95`
