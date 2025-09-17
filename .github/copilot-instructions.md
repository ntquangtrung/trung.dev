# Copilot Instructions for trung-dev

## Project Overview
- This is a Django-based personal portfolio site, styled with Tailwind CSS, and containerized using Docker.
- Continuous deployment is managed via GitHub Actions.
- The project structure is modular, with apps located in `apps/` and configuration in `config/`.

## Architecture & Key Components
- **Django Apps:** All main features are implemented as Django apps under `apps/`. Example: `apps/blog/` for blog functionality.
- **Settings:** Environment-specific settings are split into `config/settings/base.py`, `development.py`, and `production.py`.
- **Static & Templates:** Static files are in `static/`, templates in `templates/` and app-specific templates in `apps/*/templates/`.
- **Services:** External integrations (e.g., GitHub, Redis, Discord) are in `services/` and `adapters/`.
- **Theme:** Custom theme logic and assets are in `theme/`.

## Developer Workflows
- **Run locally:** Use `manage.py` for Django commands. For development, use `python manage.py runserver` or Docker Compose (`docker-compose up`).
- **Build & Deploy:** Use Docker for containerization. Deployment is automated via GitHub Actions.
- **Testing:** Tests are in `tests/` and within app folders (e.g., `apps/blog/tests.py`). Run with `python manage.py test`.
- **Static Assets:** Tailwind and other frontend assets are managed in `theme/static_src/` and built via Node.js scripts.

## Conventions & Patterns
- **App Structure:** Each app follows Django conventions, but may have extra folders like `forms/`, `model_admin/`, `tasks/`, and `context/` for separation of concerns.
- **Settings Import:** Always import settings from `config.settings`.
- **Service Adapters:** Integrations are abstracted in `adapters/` and `services/` for maintainability.
- **Environment Variables:** Sensitive config is managed via environment variables and `.env` files (not committed).

## Integration Points
- **GitHub:** Automated deployments and some features use GitHub APIs (see `adapters/github_adapter.py`, `services/github_service.py`).
- **Redis:** Used for caching or async tasks (see `services/redis.py`).
- **Discord Bot:** Custom bot logic in `services/discord/bot.py`.

## Examples
- To add a new Django app: `python manage.py startapp <appname>` and register in `config/settings/base.py`.
- To run tests: `python manage.py test` or use Docker Compose for isolated environments.
- To build static assets: Run Node.js scripts in `theme/static_src/` (see `package.json`).

## References
- Key files: `manage.py`, `config/settings/`, `apps/`, `services/`, `adapters/`, `theme/`, `static/`, `templates/`
- For more details, see the README.md and comments in config files.

---
If any section is unclear or missing, please provide feedback to improve these instructions.

## Github repository
username: <your-github-username>
repository: <your-repo-name>
