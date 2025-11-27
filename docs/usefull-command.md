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

   ---

## 7. Ruff - Linting & Formatting

1. **Check code for linting issues:**

   ```bash
   ruff check .
   ```

2. **Auto-fix linting issues:**

   ```bash
   ruff check --fix .
   ```

3. **Format code:**

   ```bash
   ruff format --check .
   ```

4. **Check specific files or directories:**

   ```bash
   ruff check path/to/file_or_directory
   ```

5. **Show configuration:**

   ```bash
   ruff check --show-settings
   ```

---

## 8. Logging with Loki & Grafana

### Development

1. **Start logging stack:**

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.logging.dev.yml up -d --build
   ```

   Or without explicitly specifying `docker-compose.override.yml` (auto-loaded):

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.logging.dev.yml up -d --build
   ```

2. **Access Grafana:**

   ```bash
   open http://localhost:4000
   # Login: admin / admin
   ```

3. **View logs in Grafana:**
   - Navigate to "Explore" (compass icon)
   - Select "Loki" datasource
   - Use LogQL queries (see examples below)

4. **Stop logging stack:**

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.logging.dev.yml down
   ```

### Common LogQL Queries

1. **View Django errors:**

   ```logql
   {container_name="django-blog-container"} |= "ERROR"
   ```

2. **View all application logs:**

   ```logql
   {app="trung-dev"}
   ```

3. **View specific service:**

   ```logql
   {service="celery-worker"}
   ```

4. **Filter by log level (JSON logs in production):**

   ```logql
   {app="trung-dev"} | json | levelname="ERROR"
   ```

5. **View Nginx access logs:**

   ```logql
   {service="nginx"}
   ```

6. **Search for specific text:**

   ```logql
   {container_name="django-blog-container"} |= "File saved"
   ```

7. **Time range filter (last 5 minutes):**

   ```logql
   {app="trung-dev"} |= "ERROR" [5m]
   ```

8. **Count errors per minute:**

   ```logql
   rate({app="trung-dev"} |= "ERROR" [1m])
   ```

### Docker Logs (Alternative - No Grafana Required)

If you want to view logs without starting the Loki/Grafana stack:

1. **View logs in real-time:**

   ```bash
   docker compose logs -f django
   ```

2. **View multiple services:**

   ```bash
   docker compose logs -f django celery-worker nginx-proxy
   ```

3. **View last 100 lines:**

   ```bash
   docker compose logs --tail=100 django
   ```

4. **Search logs:**

   ```bash
   docker compose logs django | grep ERROR
   ```

5. **Export logs:**

   ```bash
   mkdir -p logs
   docker compose logs > logs/backup-$(date +%Y%m%d).log
   ```

6. **View logs with timestamps:**

   ```bash
   docker compose logs -f -t django
   ```

### Log Retention

**Development:**
- Docker logs: 50MB × 5 files = 250MB per container
- Loki retention: 7 days

**Production:**
- Docker logs: 10MB × 3 files = 30MB per container
- Nginx logs: 20MB × 5 files = 100MB
- Loki retention: 30 days

### Pre-configured Dashboard

Access the "Trung-Dev Application Logs" dashboard:
- Go to Grafana → Dashboards
- Select "Trung-Dev Application Logs"
- View panels for Django, Errors, Celery, and Nginx logs

### Troubleshooting

1. **Grafana not accessible:**

   ```bash
   # Check if Grafana is running
   docker compose ps grafana
   
   # View Grafana logs
   docker compose logs -f grafana
   ```

2. **No logs appearing in Grafana:**

   ```bash
   # Check Promtail logs
   docker compose logs -f promtail
   
   # Check Loki logs
   docker compose logs -f loki
   
   # Verify Loki is receiving logs
   curl http://localhost:3100/ready
   ```

3. **Clean up log data:**

   ```bash
   # Stop services
   docker compose -f docker-compose.yml -f docker-compose.logging.dev.yml down
   
   # Remove log volumes
   docker volume rm simple-django-blog_loki-dev-data
   docker volume rm simple-django-blog_grafana-dev-data
   
   # Restart
   docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.logging.dev.yml up -d
   ```
