import base64
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))

from converter import convert_to_translatable_wikitext


def handler(event, context=None):
    method = (event.get("httpMethod") or "GET").upper()

    if method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    if method != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    body_raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")

    content_type = ((event.get("headers") or {}).get("content-type") or "").lower()

    if "application/json" in content_type:
        try:
            data = json.loads(body_raw)
        except (json.JSONDecodeError, ValueError):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid JSON body"}),
            }
        wikitext = data.get("wikitext", "")
    else:
        params = parse_qs(body_raw)
        wikitext = params.get("wikitext", [""])[0]

    converted = convert_to_translatable_wikitext(wikitext)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"original": wikitext, "converted": converted}),
    }
