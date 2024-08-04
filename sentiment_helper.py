import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration

# Uncomment the line below if the VADER lexicon is not already downloaded
# nltk.download('vader_lexicon')

# Initialize T5 model and tokenizer
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def analyze_sentiment_vader(text):
    """Analyze sentiment using VADER and generate short messages using T5 model."""
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

    short_message = generate_short_message(text, sentiment_message)

    return sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message

def generate_short_message(user_query, sentiment_message):
    """Generate a short message based on sentiment using T5 model."""
    if sentiment_message == 'Negative':
        prompt = f"Generate a short and uplifting message to help someone who is feeling down. User query: {user_query}"
    elif sentiment_message == 'Positive':
        prompt = f"Generate a short motivational message to reinforce someone's positive feelings. User query: {user_query}"
    else:  # Neutral sentiment
        prompt = f"Generate a short, informative message for someone with a neutral sentiment. User query: {user_query}"

    # Prepare the input text
    input_text = prompt
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    # Generate the message
    output_ids = model.generate(input_ids, max_length=50, num_return_sequences=1, early_stopping=True, num_beams=5)
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return generated_text

def gita_bot_response(user_query):
    """Generate a response based on sentiment analysis and provide a short message."""
    sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(user_query)

    # Generate a response based on sentiment
    sentiment_feedback = f"Sentiment Feedback: {sentiment_message}\n\nShort Message: {short_message}"

    return sentiment_feedback

# Example usage
if __name__ == "__main__":
    user_query = "What is the significance of meditation in the Bhagavad Gita?"
    user_query = "I am feeling enlightened after reading the Bhagavad Gita!"

    print(gita_bot_response(user_query))
