from flask import Flask, render_template, request, jsonify
from helper import generate_response
from sentiment_helper import analyze_sentiment_vader, generate_learning_message

app = Flask(__name__)


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


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    query = data.get('query', '')

    if query:
        try:
            # Perform sentiment analysis
            sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(query)
            learning_message = generate_learning_message(sentiment_message)

            # Generate chatbot response
            response_data = generate_response(query)

            if response_data:
                response = {
                    "status": "success",
                    "general_response": response_data.get("general_response", "Sorry, I can't answer this query."),
                    "dataset_response": response_data.get("dataset_response", ""),
                    "id": response_data.get("id", ""),
                    "shloka": response_data.get("shloka", ""),
                    "hin_meaning": response_data.get("hin_meaning", ""),
                    "eng_meaning": response_data.get("eng_meaning", ""),
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
                    "message": "Sorry, I can't answer this query."
                }
        except Exception as e:
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
    app.run(debug=True)
