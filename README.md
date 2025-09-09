## Alexa Compliments Skill (Lambda + OpenAI)

### Overview
This skill returns a single, family‑friendly compliment using OpenAI. Code is written for AWS Lambda using the Alexa Skills Kit SDK for Python.

### Files
- `lambda_function.py`: Main skill handler (Lambda entry point `lambda_handler`).
- `utils_s3.py`: Helper to generate S3 presigned URLs (optional).
- `alexa-model.json`: Interaction model for import to the Alexa Developer Console.
- `skill-package/`: ASK CLI skill package (manifest + interaction model).
- `ask-resources.json`: ASK CLI config for the skill package.
- `.github/workflows/deploy.yml`: CI to deploy Lambda + Skill.
- `Makefile`: common local tasks (package, deploy via ASK CLI).
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

### ASK CLI (optional)
Prereqs: Node 18+, `ask-cli@2`, and you have a Vendor ID.

1. Configure ASK locally: `make ask-login`
2. Render manifest with your Lambda ARN:
   - `export LAMBDA_ARN=arn:aws:lambda:REGION:ACCOUNT:function:FUNCTION_NAME`
   - `python scripts/render_skill_manifest.py`
3. Deploy the skill package: `npx ask-cli@2 deploy -p default`

### CI/CD
`deploy.yml` expects these GitHub Secrets:
- `AWS_ROLE_ARN`, `AWS_REGION`, `LAMBDA_FUNCTION_NAME`
- `LAMBDA_ARN` (the ARN used in the skill manifest)
- `ASK_REFRESH_TOKEN`, `ASK_VENDOR_ID`, `ASK_SKILL_ID`

### Testing
- Try: "Open daily compliment" or "give me a compliment".
- If OpenAI is unavailable, the skill replies with a safe fallback message.

### Security
- Never hardcode secrets. Use Lambda environment variables and rotate keys routinely.

### Tips to grow usage
- Choose a short, memorable invocation name (e.g., “Daily Compliment”).
- Add diverse sample utterances in `interactionModels` to cover phrasings.
- Keep responses concise and upbeat; avoid repetition with a slightly higher temperature.
- Encourage re‑engagement: add a card or a follow‑up prompt occasionally.
- Enable optional follow‑up prompts by setting `FOLLOWUP_RATE=1` and Alexa built‑in intents `AMAZON.YesIntent`/`AMAZON.NoIntent` are supported.
- A/B prompts: set `AB_FORCE_VARIANT=A` or `B` for testing; otherwise users are split consistently.
- Metrics: CloudWatch namespace is controlled by `METRICS_NAMESPACE` (default `ComplimentsSkill`).

### Localization
Skill package includes `en-US`, `en-GB`, `en-CA`, `en-AU` models. Update invocation names per locale if desired and redeploy with ASK CLI.


