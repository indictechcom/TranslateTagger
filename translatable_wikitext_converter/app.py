from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  # Import flask-cors

from .wikitranslator import tag_for_translation

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/convert', methods=['GET'])
def redirect_to_home():
    return render_template('home.html')

@app.route('/convert', methods=['POST'])
def convert():
    wikitext = request.form.get('wikitext', '')
    tagged = tag_for_translation(wikitext)
    return render_template('home.html', original=wikitext, converted=tagged)

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
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'wikitext' not in data:
            return jsonify({'error': 'Missing "wikitext" in JSON payload'}), 400
        
        wikitext = data.get('wikitext', '')
        converted_text = convert_to_translatable_wikitext(wikitext)
        
        return jsonify({
            'original': wikitext,
            'converted': converted_text
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
