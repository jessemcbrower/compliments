## Alexa Compliments Skill

### Overview
An Alexa skill that delivers a single, family‑friendly compliment. Runs on AWS Lambda using the Alexa Skills Kit SDK for Python.

### Files
- `lambda_function.py`: main skill handler (entry `lambda_handler`).
- `skill-package/`: skill manifest + interaction models (ASK CLI).
- `requirements.txt`, `Makefile`, `.github/workflows/deploy.yml`.

### Setup
1. Create a Lambda function (Python 3.11 or 3.10).
2. Environment variables:
   - `OPENAI_API_KEY` (required)
   - `OPENAI_MODEL` (optional)
   - `OPENAI_MAX_TOKENS` (optional)
   - `FOLLOWUP_RATE` (optional)
   - `USER_PREFS_TABLE` (optional)
3. Build the package locally:
   - Create a virtualenv and install `requirements.txt`.
   - Zip contents (including dependencies) and upload to Lambda, or use a Lambda layer.

### Alexa Developer Console
1. Create a new skill or update your existing one.
2. Import from `skill-package/` (or use ASK CLI below).
3. Set endpoint to your Lambda ARN in the same region.
4. Save and build the model.

### ASK CLI (optional)
1. Configure: `make ask-login`
2. Set ARN and render: `export LAMBDA_ARN=... && python scripts/render_skill_manifest.py`
3. Deploy: `npx ask-cli@2 deploy -p default`

### CI/CD
`deploy.yml` reads standard AWS and ASK credentials plus required app settings.

### Testing
- Try: "Open daily compliment" or "give me a compliment".

### Security
- Set secrets as Lambda environment variables; rotate routinely.

### Localization
Includes `en-US`, `en-GB`, `en-CA`, `en-AU` models.
Advanced options are in `docs/ADVANCED.md`.


