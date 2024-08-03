import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download the VADER lexicon
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

    # Format the response
    response = (f"Query: {query}\n"
                f"compound: {compound_percentage:.2f}%, neg: {neg_percentage:.2f}%, "
                f"neu: {neu_percentage:.2f}%, pos: {pos_percentage:.2f}%,\n"
                f"Sentiment Analysis Complete!")

    return response, compound_percentage, neg_percentage, neu_percentage, pos_percentage


# Example usage in GitaBot
def gita_bot_response(user_query):
    response, compound_percentage, neg_percentage, neu_percentage, pos_percentage = analyze_sentiment_vader(user_query)

    # Generate a response based on sentiment
    if compound_percentage >= 50:
        sentiment_feedback = "It seems like you're in a positive mood!"
    elif compound_percentage <= 50:
        sentiment_feedback = "It seems like you're feeling a bit down."
    else:
        sentiment_feedback = "Your mood seems neutral."

    return f"{response}\n\nSentiment Feedback: {sentiment_feedback}"


# Example usage
user_query = "I am feeling enlightened after reading the Bhagavad Gita!"
print(gita_bot_response(user_query))
