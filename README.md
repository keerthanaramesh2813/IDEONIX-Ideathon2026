# SafeStudent — Intelligent Digital Safety MVP

A runnable prototype for an AWS-oriented student digital safety platform.

## What works
- Student safety dashboard
- Message / URL analysis
- Phishing, scam, cyberbullying, harassment and privacy-risk detection
- 0–100 risk scoring
- Safety recommendation
- Incident storage in memory
- Admin dashboard
- Incident resolution

## Run locally

Python 3.10+ recommended.

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## AWS upgrade path

Replace the local `analyze_content()` function with an AWS Lambda function calling Amazon Bedrock. Replace the in-memory `INCIDENTS` list with DynamoDB. Put API Gateway in front of Lambda, Cognito in front of protected routes, S3/CloudFront in front of the frontend, and SNS for high-risk notifications.

This local version intentionally does not claim to be a production safety system. It is a demo/MVP.
