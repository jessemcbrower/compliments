## Advanced Options

### Environment Variables
- `OPENAI_MODEL`, `OPENAI_MAX_TOKENS`
- `FOLLOWUP_RATE` (0 or 1)
- `AB_FORCE_VARIANT` (A or B)
- `USER_PREFS_TABLE` (DynamoDB table for opt-in/out)
- `METRICS_NAMESPACE` (CloudWatch namespace)

### Follow-up Preferences
Create a DynamoDB table with primary key `pk` (String). Set `USER_PREFS_TABLE` to this table name.
Users can say:
- "enable follow ups" to opt in
- "disable follow ups" to opt out

### Deployment
- Makefile target `package` builds a zip suitable for Lambda upload.
- CI workflow deploys Lambda and the skill package via ASK CLI.


