## Summary

<!-- Briefly describe what this PR accomplishes -->

## Pre-Merge Checklist

### Code Quality
- [ ] Code follows project style guidelines (Ruff linting passes)
- [ ] Code is formatted with `ruff format .`
- [ ] No unused imports or variables
- [ ] Type hints added where appropriate

### Django & Python
- [ ] Poetry dependencies added/updated if needed
- [ ] `requirements.txt` regenerated if `poetry.lock` changed
- [ ] Environment variables documented (if new ones added)
- [ ] Django admin tested (if models/admin changed)
- [ ] Custom storage/Celery tasks tested (if applicable)

### Security & Performance
- [ ] No sensitive data exposed (secrets, tokens, passwords)
- [ ] SQL queries optimized (no N+1 queries)
- [ ] Proper error handling added
- [ ] Input validation implemented

### Docker & Deployment
- [ ] Docker build succeeds
- [ ] Entrypoint script tested (if modified)
- [ ] Environment variables set correctly
- [ ] No breaking changes to deployment process

## Additional Notes

<!-- Any additional context, concerns, or questions -->
