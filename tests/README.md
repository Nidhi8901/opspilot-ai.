# OpsPilot test notes

These tests are intentionally safe for local development and CI.

They verify the running API and PostgreSQL-backed endpoints without making
a paid Amazon Bedrock generation request.

Default target:

    http://127.0.0.1:8000

Override it with:

    OPSPILOT_BASE_URL=http://host:port pytest

The AI POST endpoint is not called by the smoke suite. Bedrock should be
tested separately with a mocked client in unit tests or an explicitly
enabled integration test.
