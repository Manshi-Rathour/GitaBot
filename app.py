from flask import Flask, render_template, request, jsonify
from helper import generate_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('gitabot.html')


@app.route('/gitabot', methods=['POST'])
def chatbot():
    user_message = request.json.get("message")

    if user_message:
        try:
            # Generate chatbot response
            response_data = generate_response(user_message)

            # Check if the response data contains required fields
            if response_data:
                return jsonify({
                    "general_response": response_data.get("general_response", "Sorry, I can't answer this query."),
                    "dataset_response": response_data.get("dataset_response", ""),
                    "id": response_data.get("id", ""),
                    "shloka": response_data.get("shloka", ""),
                    "hin_meaning": response_data.get("hin_meaning", ""),
                    "eng_meaning": response_data.get("eng_meaning", "")
                })
            else:
                return jsonify({"message": "Sorry, I can't answer this query."})

        except Exception as e:
            # Log the error for debugging
            app.logger.error("An error occurred: %s", str(e))
            return jsonify({"message": "An error occurred while processing your request."})
    else:
        return jsonify({"message": "No query received."})


if __name__ == "__main__":
    app.run(debug=True)
