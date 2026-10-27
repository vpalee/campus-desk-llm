# Q3 live app deployment

Deploy the repository as a Render **Web Service** using the **Free** instance type. No database, disk, paid compute, or custom domain is required.

## Settings

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/vpalee/campus-desk-llm` |
| Branch | `main` |
| Root directory | blank (repository root) |
| Runtime | Python 3 |
| Build | `pip install -r requirements.lock` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health path | `/api/health` |
| Python version | `3.13.13` |
| Auto deploy | Off; deploy reviewed commits manually |

The same settings are defined in `render.yaml` for Blueprint deployment.

## Server environment

- `PYTHON_VERSION=3.13.13`
- `PUBLIC_DEMO=1`
- `OPENAI_BASE_URL=https://llm.nat-d.uk/v1`
- `OPENAI_API_KEY`: the owner's existing class-proxy key, stored only in Render's environment secret field. Do not commit or log it.

The UI calls only its own `/api/ask` endpoint. The server calls the required Gemma model using the OpenAI SDK. Visitors never receive the key. No authentication is added to the demo, so anyone with its URL can try the fictional handbook within the workload budget.

## Workload budget

With `PUBLIC_DEMO=1`, requests reserve a slot before model use. The process accepts at most two simultaneous questions, 30 per rolling hour, and 120 per rolling day. The lock protects reservations across server threads. Failed model calls remain counted. Busy or exhausted requests return HTTP 429 and a retry interval; handbook browsing and health checks remain available.

These counters are in memory, reset on restart, and are not shared between processes. Keep one worker. They reduce casual excess traffic but are not authentication, a durable quota, a distributed abuse defense, or a provider billing cap. The existing four-round/six-tool-call bounds and 1,200-token response limit remain in force.

## Verification before submitting the URL

1. Confirm the Render deployment is live on HTTPS and uses the Free instance type.
2. Check `/api/health`: `configured` and `public_demo` should both be true, with 16 articles and model `gemma-4-E4B-it`. This verifies configuration, not remote model reachability.
3. Submit a real new-phone/MFA question in the deployed UI and inspect the answer and source article.
4. Submit an out-of-scope question and inspect its abstention. Also inspect an honest failure or limitation, such as the injection case retained in `evaluation/live_results_v2.json`; model behavior may vary between runs.
5. Confirm model errors and budget errors are displayed clearly and no credential appears in responses, page source, or assets.
6. Submit only the working deployed URL to Q3 and verify the course records it.

The original offline results remain retrieval-only evidence. Deployment does not turn them into an answer-faithfulness score. The fictional policies still require institution approval before real use.

## Free host limitations

Render Free web services can spin down after 15 idle minutes and take about a minute to wake. Their filesystem is ephemeral. This application does not require persistent writes. Free service hours, build minutes, and outbound traffic remain subject to Render's account limits. Do not add a payment method or select a paid instance for this coursework deployment.

Official references: [FastAPI deployment](https://render.com/docs/deploy-fastapi), [Free instances](https://render.com/docs/free), [Python version](https://render.com/docs/python-version), and [Blueprint format](https://render.com/docs/blueprint-spec).
