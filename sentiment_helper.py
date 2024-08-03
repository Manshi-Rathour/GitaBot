import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download the VADER lexicon if not already downloaded
nltk.download('vader_lexicon')

def analyze_sentiment_vader(query):
    # Initialize the VADER sentiment intensity analyzer
    sia = SentimentIntensityAnalyzer()

    # Get the sentiment scores
    sentiment_scores = sia.polarity_scores(query)

    # Extract the sentiment components
    compound = sentiment_scores['compound']
    neg = sentiment_scores['neg']
    neu = sentiment_scores['neu']
    pos = sentiment_scores['pos']

    # Convert sentiment scores to percentage
    compound_percentage = (compound + 1) * 50
    neg_percentage = neg * 100
    neu_percentage = neu * 100
    pos_percentage = pos * 100

    # Generate a sentiment message based on the compound score
    if compound >= 0.05:
        sentiment_message = "The sentiment of this query is positive."
    elif compound <= -0.05:
        sentiment_message = "The sentiment of this query is negative."
    else:
        sentiment_message = "The sentiment of this query is neutral."

    # Format the response
    response = (f"Sentiment Analysis Report:\n"
                f"- Compound Score: {compound_percentage:.2f}%\n"
                f"- Negative Sentiment: {neg_percentage:.2f}%\n"
                f"- Neutral Sentiment: {neu_percentage:.2f}%\n"
                f"- Positive Sentiment: {pos_percentage:.2f}%\n"
                f"\n{sentiment_message}\n"
                f"Analysis complete.")

    return response, compound_percentage, neg_percentage, neu_percentage, pos_percentage, sentiment_message

def gita_bot_response(user_query):
    response, compound_percentage, neg_percentage, neu_percentage, pos_percentage, sentiment_message = analyze_sentiment_vader(user_query)

    # Generate a response based on sentiment
    sentiment_feedback = sentiment_message

    return f"{response}\n\nSentiment Feedback: {sentiment_feedback}"

# Example usage
user_query = "I am feeling enlightened after reading the Bhagavad Gita!"
print(gita_bot_response(user_query))