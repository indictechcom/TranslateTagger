import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import app as flask_app


def handler(event, context=None):
    headers = dict((event.get("headers") or {}).items())
    method = (event.get("httpMethod") or "GET").upper()
    path = event.get("path") or "/"
    query_params = event.get("queryStringParameters") or {}
    body = event.get("body") or ""

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    client = flask_app.test_client()
    response = client.open(
        path,
        method=method,
        data=body,
        query_string=query_params,
        headers=headers,
    )

    return {
        "statusCode": response.status_code,
        "headers": {key: value for key, value in response.headers.items()},
        "body": response.get_data(as_text=True),
    }
