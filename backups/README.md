Backups are stored locally under `.secrets/lambda/` and are not committed.

Contents (local only):
- `.secrets/lambda/code.zip` — downloaded Lambda deployment package
- `.secrets/lambda/get-function.json` — prior Lambda metadata

To refresh backups:
- `make backup-skill` (safe; no secrets)
- `make backup-lambda` (downloads code to `.secrets/lambda/`)

