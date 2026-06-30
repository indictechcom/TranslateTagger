from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import requests as http_requests
from datetime import datetime

from converter import convert_to_translatable_wikitext, process_double_brackets  # noqa: F401

app = Flask(__name__)
CORS(app)

CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://tools-static.wmflabs.org; "
    "style-src 'self' 'unsafe-inline' https://tools-static.wmflabs.org; "
    "connect-src 'self' https://tools-static.wmflabs.org; "
    "img-src 'self' data:; "
    "font-src 'self' https://tools-static.wmflabs.org data:"
)


def get_last_updated_date():
    try:
        resp = http_requests.get(
            "https://api.github.com/repos/indictechcom/translatable-wikitext-converter/commits",
            timeout=5,
        )
        data = resp.json()
        if data and isinstance(data, list) and len(data) > 0:
            raw = data[0]["commit"]["committer"]["date"]
            dt = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ")
            return dt.strftime("%B %-d, %Y")
    except Exception:
        pass
    return "Unavailable"


@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = CSP_POLICY
    return response


@app.route('/')
def index():
    return render_template('home.html', last_updated=get_last_updated_date())


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/convert', methods=['GET'])
def redirect_to_home():
    return render_template('home.html', last_updated=get_last_updated_date())


@app.route('/convert', methods=['POST'])
def convert():
    wikitext = request.form.get('wikitext', '')
    converted_text = convert_to_translatable_wikitext(wikitext)
    return render_template('home.html', original=wikitext, converted=converted_text,
                           last_updated=get_last_updated_date())


@app.route('/api/convert', methods=['GET', 'POST'])
def api_convert():
    if request.method == 'GET':
        return """
        <h1>Translate Tagger API</h1>
        <p>Send a POST request with JSON data to use this API.</p>
        <p>Example:</p>
        <pre>
        curl -X POST https://translatetagger.toolforge.org/api/convert \\
        -H "Content-Type: application/json" \\
        -d '{"wikitext": "This is a test [[link|example]]"}'
        </pre>
        """
    data = request.get_json()
    if not data or 'wikitext' not in data:
        return jsonify({'error': 'Missing "wikitext" in JSON payload'}), 400
    wikitext = data.get('wikitext', '')
    converted_text = convert_to_translatable_wikitext(wikitext)
    return jsonify({'original': wikitext, 'converted': converted_text})


if __name__ == '__main__':
    app.run(debug=True)
