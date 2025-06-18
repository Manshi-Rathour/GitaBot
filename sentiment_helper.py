import nltk
import random
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load VADER lexicon from local path instead of downloading
vader_lexicon_path = "./vader_lexicon/vader_lexicon.txt"
analyzer = SentimentIntensityAnalyzer(lexicon_file=vader_lexicon_path)

# Predefined quotes for different sentiments
positive_quotes = [
    "Your positive energy is a beacon of light, inspiring those around you. Keep shining!",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "Positive thinking will let you do everything better than negative thinking will.",
    "Every day is a new beginning. Take a deep breath, smile, and start again.",
    "Keep your face always toward the sunshine—and shadows will fall behind you.",
    "The best way to predict the future is to create it.",
    "Believe you can and you're halfway there.",
    "You are never too old to set another goal or to dream a new dream.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "The only way to achieve the impossible is to believe it is possible.",
    "Happiness is not something ready-made. It comes from your own actions.",
    "In the middle of every difficulty lies opportunity.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Act as if what you do makes a difference. It does.",
    "With the new day comes new strength and new thoughts."
]

negative_quotes = [
    "Even in challenging times, remember that every sunset brings the promise of a new dawn.",
    "Tough times never last, but tough people do.",
    "In the midst of winter, I found there was, within me, an invincible summer.",
    "The greatest glory in living lies not in never falling, but in rising every time we fall.",
    "When you reach the end of your rope, tie a knot in it and hang on.",
    "Hardships often prepare ordinary people for an extraordinary destiny.",
    "The darkest hour has only sixty minutes.",
    "Stars can't shine without darkness.",
    "Although the world is full of suffering, it is also full of the overcoming of it.",
    "Turn your wounds into wisdom.",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
    "Our greatest glory is not in never falling, but in rising every time we fall.",
    "Strength does not come from physical capacity. It comes from an indomitable will.",
    "The struggle you're in today is developing the strength you need for tomorrow.",
    "When everything seems to be going against you, remember that the airplane takes off against the wind, not with it."
]

neutral_quotes = [
    "Embrace the calmness within you, for it is in stillness that we find clarity and strength.",
    "Life is a balance of holding on and letting go.",
    "Every day may not be good, but there is something good in every day.",
    "Sometimes you will never know the value of a moment until it becomes a memory.",
    "Keep your eyes on the stars and your feet on the ground.",
    "The best way to find yourself is to lose yourself in the service of others.",
    "Life is not measured by the number of breaths we take, but by the moments that take our breath away.",
    "Life is 10% what happens to us and 90% how we react to it.",
    "The only journey is the one within.",
    "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment.",
    "Life is what happens when you're busy making other plans.",
    "It does not matter how slowly you go as long as you do not stop.",
    "The purpose of our lives is to be happy.",
    "You have within you right now, everything you need to deal with whatever the world can throw at you.",
    "Life is really simple, but we insist on making it complicated."
]


def analyze_sentiment_vader(text):
    """Analyze sentiment using VADER and generate short messages based on predefined quotes."""
    sentiment_scores = analyzer.polarity_scores(text)

    compound = sentiment_scores['compound']
    neg = sentiment_scores['neg']
    neu = sentiment_scores['neu']
    pos = sentiment_scores['pos']

    if compound >= 0.05:
        sentiment_message = "Positive"
    elif compound <= -0.05:
        sentiment_message = "Negative"
    else:
        sentiment_message = "Neutral"

    short_message = generate_short_message(sentiment_message)

    return sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message


def generate_short_message(sentiment_message):
    """Generate a short, quotable message based on sentiment using predefined quotes."""
    if sentiment_message == 'Negative':
        return random.choice(negative_quotes)
    elif sentiment_message == 'Positive':
        return random.choice(positive_quotes)
    else:
        return random.choice(neutral_quotes)


def generate_learning_message(sentiment_message):
    """Generate a learning message based on sentiment."""
    if sentiment_message == 'Negative':
        return "Reflect on challenges and remember that every setback is an opportunity to grow stronger. Embrace the lessons learned from difficult experiences."
    elif sentiment_message == 'Positive':
        return "Harness your positive energy to set new goals and inspire others. Your optimism can lead to remarkable achievements and influence those around you."
    else:
        return "Maintain your balance and stay grounded. Use this time to reflect on your progress and plan your next steps with clarity and purpose."


def generate_all_messages():
    """Generate sentiment analysis results and messages for a set of example texts."""
    example_texts = [
        "I am feeling enlightened after reading the Bhagavad Gita!",
        "I am really frustrated with the way things are going.",
        "It’s just another day, nothing special.",
        "Today is a wonderful day full of opportunities!",
        "I can't seem to get anything right today.",
        "I have a lot on my mind but I'm staying calm.",
        "Feeling great about the new project I'm working on!",
        "Facing some challenges, but I believe things will get better.",
        "I am indifferent to what’s happening around me."
    ]

    for text in example_texts:
        sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(text)
        learning_message = generate_learning_message(sentiment_message)

        print(f"Text: {text}")
        print(f"Sentiment Scores: {sentiment_scores}")
        print(f"Compound Score: {compound:.2f}")
        print(f"Negative Score: {neg:.2f}")
        print(f"Neutral Score: {neu:.2f}")
        print(f"Positive Score: {pos:.2f}")
        print(f"Sentiment Message: {sentiment_message}")
        print(f"Short Message: {short_message}")
        print(f"Learning Message: {learning_message}")
        print("-" * 50)


if __name__ == "__main__":
    generate_all_messages()
