## Alexa Compliments Skill (Lambda + OpenAI)

### Overview
This skill returns a single, family‑friendly compliment using OpenAI. Code is written for AWS Lambda using the Alexa Skills Kit SDK for Python.

### Files
- `lambda_function.py`: Main skill handler (Lambda entry point `lambda_handler`).
- `utils_s3.py`: Helper to generate S3 presigned URLs (optional).
- `alexa-model.json`: Interaction model for import to the Alexa Developer Console.
- `requirements.txt`: Python dependencies.

### Setup
1. Create a Lambda function (Python 3.11 or 3.10).
2. Set environment variables:
   - `OPENAI_API_KEY` (required)
   - `OPENAI_MODEL` (optional, default `gpt-4o-mini`)
   - `OPENAI_MAX_TOKENS` (optional, default `64`)
   - `S3_PERSISTENCE_BUCKET`, `S3_PERSISTENCE_REGION` (optional, for `utils_s3.py`)
3. Build the package locally:
   - Create a virtualenv and install `requirements.txt`.
   - Zip contents (including dependencies) and upload to Lambda, or use a Lambda layer.

### Alexa Developer Console
1. Create a new skill or update your existing one.
2. Import `alexa-model.json` into your interaction model.
3. Set endpoint to your Lambda ARN in the same region.
4. Save and build the model.

### Testing
- Try: "Open daily compliment" or "give me a compliment".
- If OpenAI is unavailable, the skill replies with a safe fallback message.

### Security
- Never hardcode secrets. Use Lambda environment variables and rotate keys routinely.


