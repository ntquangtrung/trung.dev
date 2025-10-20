# Django By Example - Blog Project

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

   _(`deactivate` to deactivate the virtual environment.)_

4. _(Optional)_ Install all dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   _(If you already have a `requirements.txt` file.)_

5. _(Optional)_ Save installed packages to `requirements.txt`:

   ```bash
   pip freeze > requirements.txt
   ```

6. _(Optional)_ Uninstall all packages listed in `requirements.txt`:

   ```bash
   pip uninstall -r requirements.txt -y
   ```

7. _(Poetry)_ Install project dependencies:

   ```bash
   poetry install
   ```

8. _(Poetry)_ Add a new dependency:

    ```bash
    poetry add <package-name>
    ```

9. _(Poetry)_ Remove a dependency:

    ```bash
    poetry remove <package-name>
    ```
10. _(Poetry)_ Show outdated packages:

    ```bash
    poetry show --outdated
    ```

11. _(Poetry)_ Update packages:

    ```bash
    poetry update <package-A> <package-B>
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

   _(`exit()` or `quit()` to close the shell.)_

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
"weasyprint (>=66.0,<67.0)",
   or

   ```bash
   python3 manage.py makemigrations --settings=config.settings.development
   ```

3. Apply migrations:

   ```bash
   python3 manage.py migrate <app_name|optional> --settings=config.settings.development
   ```

---

## 4. Docker

1. Build docker compose

   ```bash
   docker compose build
   ```

2. Run docker compose

   ```bash
   docker compose up -d
   ```

3. Remove docker container and django image

   ```bash
   docker compose down --remove-orphans
   ```

   or remove both containers and images

   ```bash
   docker compose down --rmi local --remove-orphans
   ```

4. Build and run container for development

   ```bash
   docker compose up -d --build
   ```

5. Build for production

   ```bash
   docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build -d
   ```

---

## 5. Django Tailwind Common Commands

1. Install Tailwind app dependencies:

   ```bash
   python3 manage.py tailwind install
   ```

2. Start Tailwind development server (watch for changes):

   ```bash
   python3 manage.py tailwind start
   ```

3. Build Tailwind CSS for production:

   ```bash
   python3 manage.py tailwind build
   ```

4. Check Tailwind configuration:

   ```bash
   python3 manage.py tailwind check
   ```

---

## 6. Django Test Runner

1. **Run Django Tests**

   Execute:

   ```bash
   python3 manage.py test --pattern="*.test.py" --settings=config.settings.development
   ```

   Confirm all tests in files matching `*.test.py` are discovered and executed.
