import os
import re
import html
import json
from flask import Flask, render_template, request, jsonify
from helper import generate_response
from sentiment_helper import analyze_sentiment_vader, generate_learning_message
from google.cloud import translate_v2 as translate

app = Flask(__name__)

# Path to Google Cloud credentials
credentials_file = 'advance-stratum-409704-8f6e8f9201b9.json'  # For contributor 1
# credentials_file = 'gitabot-434209-8f7a7daa37c1.json'  # For contributor 2

credentials_path = os.path.join(os.path.dirname(__file__), credentials_file)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Initialize Google Cloud Translation client
translate_client = translate.Client()

# Only these two languages are supported anywhere in the app
SUPPORTED_LANGUAGES = {'en', 'hi'}

FALLBACK_MESSAGE = {
    'en': "Sorry, I can't answer this query.",
    'hi': "क्षमा करें, मैं इस प्रश्न का उत्तर नहीं दे सकता।"
}

TABLE_SEPARATOR_RE = re.compile(r'^\s*\|?[\s:\-|]+\|?\s*$')


def _translate_batch(texts, source_language, target_language):
    """Translate a list of strings in one API call, unescape HTML entities
    that the Translate API tends to introduce (&#39; etc.), and return the
    translated strings in the same order."""
    if not texts:
        return []
    results = translate_client.translate(
        texts, source_language=source_language, target_language=target_language
    )
    # translate() returns a single dict if given a single string and a list
    # of dicts if given a list — we always pass a list, so normalize just in case.
    if isinstance(results, dict):
        results = [results]
    return [html.unescape(r['translatedText']) for r in results]


def translate_markdown(text, target_language, source_language='en'):
    """
    Translate a markdown string while preserving its structure.

    Translating a whole multi-paragraph markdown blob in a single Translate
    API call causes newlines to be stripped, which destroys headers, tables,
    and blockquotes. Instead, translate line-by-line (and cell-by-cell for
    table rows), then rejoin with the original line breaks so markdown
    formatting survives.
    """
    if not text or target_language == source_language:
        return text

    lines = text.split('\n')

    # Collect the pieces that actually need translation, tagged with where
    # they go back into the reconstructed output.
    plain_line_jobs = []   # (line_index, text)
    table_cell_jobs = []   # (line_index, cell_index, text)

    parsed_rows = {}  # line_index -> list of cells (for table rows)

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        # Table separator rows like "|---|---|" or "---|---" — leave as-is.
        if TABLE_SEPARATOR_RE.match(stripped):
            continue

        # Table data rows — translate each cell separately so pipes and
        # column alignment survive.
        if '|' in stripped:
            leading = '|' if stripped.startswith('|') else ''
            trailing = '|' if stripped.endswith('|') else ''
            inner = stripped
            if leading:
                inner = inner[1:]
            if trailing:
                inner = inner[:-1]
            cells = inner.split('|')
            parsed_rows[i] = {'leading': leading, 'trailing': trailing, 'cells': cells}
            for c_idx, cell in enumerate(cells):
                if cell.strip():
                    table_cell_jobs.append((i, c_idx, cell.strip()))
            continue

        # Normal line (paragraph, heading, blockquote, list item, etc.)
        # Markdown prefix markers (#, >, -, 1., etc.) are kept and only the
        # text after them is translated, so the markers don't get mangled.
        prefix_match = re.match(r'^(\s*(#{1,6}|>|[-*+]|\d+\.)\s+)', line)
        prefix = prefix_match.group(1) if prefix_match else ''
        content = line[len(prefix):]
        if content.strip():
            plain_line_jobs.append((i, prefix, content))

    # Batch-translate everything in as few API calls as possible.
    plain_texts = [content for (_, _, content) in plain_line_jobs]
    plain_translated = _translate_batch(plain_texts, source_language, target_language)

    cell_texts = [text for (_, _, text) in table_cell_jobs]
    cell_translated = _translate_batch(cell_texts, source_language, target_language)

    # Rebuild plain/heading/blockquote/list lines.
    for (i, prefix, _), translated in zip(plain_line_jobs, plain_translated):
        lines[i] = prefix + translated

    # Rebuild table rows.
    cell_results_by_line = {}
    for (i, c_idx, _), translated in zip(table_cell_jobs, cell_translated):
        cell_results_by_line.setdefault(i, {})[c_idx] = translated

    for i, row in parsed_rows.items():
        cells = row['cells']
        translated_cells = [
            cell_results_by_line.get(i, {}).get(c_idx, cell.strip())
            for c_idx, cell in enumerate(cells)
        ]
        rebuilt = '|'.join(f' {c} ' for c in translated_cells)
        lines[i] = row['leading'] + rebuilt + row['trailing']

    return '\n'.join(lines)


# Load supported languages from JSON file
def load_supported_languages():
    try:
        with open('languages.json', 'r', encoding='utf-8') as file:
            languages = json.load(file)
        filtered = [lang for lang in languages if lang.get('code') in SUPPORTED_LANGUAGES]
        return filtered if filtered else [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "हिन्दी (Hindi)"}
        ]
    except Exception as e:
        print("Error loading languages from JSON file:", e)
        return [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "हिन्दी (Hindi)"}
        ]


supported_languages = load_supported_languages()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gitabot')
def gitabot():
    return render_template('gitabot.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/get_languages')
def get_languages():
    try:
        return jsonify(supported_languages)
    except Exception as e:
        print("Error fetching supported languages:", e)
        return jsonify([])


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    query = data.get('query', '')

    language = data.get('language') or data.get('input_language', 'en')
    if language not in SUPPORTED_LANGUAGES:
        language = 'en'

    if query:
        try:
            # Translate query to English if it's not already in English
            # (a short single-line query — no markdown structure to preserve)
            if language != 'en':
                query = translate_client.translate(
                    query,
                    source_language=language,
                    target_language='en'
                )['translatedText']

            # Perform sentiment analysis
            sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(query)
            learning_message = generate_learning_message(sentiment_message)

            # Generate chatbot response
            response_data = generate_response(query)

            if response_data:
                chatbot_response = response_data.get("general_response", FALLBACK_MESSAGE[language])

                # Translate response back to Hindi, preserving markdown structure
                if language != 'en':
                    chatbot_response = translate_markdown(chatbot_response, language)

                meaning = response_data.get(
                    "hin_meaning" if language == 'hi' else "eng_meaning", ""
                )

                response = {
                    "status": "success",
                    "language": language,
                    "general_response": chatbot_response,
                    "dataset_response": response_data.get("dataset_response", ""),
                    "id": response_data.get("id", ""),
                    "shloka": response_data.get("shloka", ""),
                    "hin_meaning": response_data.get("hin_meaning", ""),
                    "eng_meaning": response_data.get("eng_meaning", ""),
                    "meaning": meaning,
                    "sentiment": {
                        'compound': compound,
                        'neg': neg,
                        'neu': neu,
                        'pos': pos,
                        'message': sentiment_message,
                        'short_message': short_message,
                        'learning_message': learning_message
                    }
                }
            else:
                response = {
                    "status": "failure",
                    "message": FALLBACK_MESSAGE[language]
                }
        except Exception as e:
            print(f"Error processing request: {e}")
            response = {
                "status": "error",
                "message": "An error occurred while processing your request."
            }
    else:
        response = {
            "status": "failure",
            "message": "Query cannot be empty."
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)