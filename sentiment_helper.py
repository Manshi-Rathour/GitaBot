import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Download the VADER lexicon if not already downloaded
# nltk.download('vader_lexicon')

# Initialize Hugging Face text generation pipeline
text_generator = pipeline("text-generation", model="gpt2")

def analyze_sentiment_vader(text):
    """Analyze sentiment using VADER and generate detailed feedback using Hugging Face model."""
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)

    compound = sentiment_scores['compound']
    neg = sentiment_scores['neg']
    neu = sentiment_scores['neu']
    pos = sentiment_scores['pos']

    # Determine overall sentiment message
    if compound >= 0.05:
        sentiment_message = "Positive"
    elif compound <= -0.05:
        sentiment_message = "Negative"
    else:
        sentiment_message = "Neutral"

    detailed_feedback = generate_detailed_feedback(text, sentiment_message)

    return sentiment_scores, compound, neg, neu, pos, sentiment_message, detailed_feedback

def generate_short_message(user_query, sentiment_message):
    """Generate a short message based on sentiment."""
    if sentiment_message == 'Negative':
        prompt = f"Generate a short and uplifting message to help someone who is feeling down: {user_query}"
    elif sentiment_message == 'Positive':
        prompt = f"Generate a short motivational message to reinforce someone's positive feelings: {user_query}"
    else:  # Neutral sentiment
        prompt = f"Generate a short, informative message for someone with a neutral sentiment: {user_query}"

    # Generate the response
    response = text_generator(prompt, max_length=200, num_return_sequences=1, truncation=True)

    # Extract the generated text from the response
    generated_text = response[0]['generated_text'].strip()

    return generated_text

def generate_detailed_feedback(user_query, sentiment_message):
    """Generate detailed feedback based on the user's query and sentiment analysis result."""
    # Generate motivational or informative response based on sentiment
    detailed_feedback = generate_short_message(user_query, sentiment_message)

    return detailed_feedback

def gita_bot_response(user_query):
    """Generate a response based on sentiment analysis and provide detailed feedback."""
    sentiment_scores, compound, neg, neu, pos, sentiment_message, detailed_feedback = analyze_sentiment_vader(
        user_query)

    # Generate a response based on sentiment
    sentiment_feedback = f"Sentiment Feedback: {sentiment_message}\n\nDetailed Feedback: {detailed_feedback}"

    return sentiment_feedback

# Example usage
if __name__ == "__main__":
    user_query = "I am feeling enlightened after reading the Bhagavad Gita!"
    print(gita_bot_response(user_query))
