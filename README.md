# GitaBot

## Introduction
Welcome to **GitaBot**, an advanced interactive chatbot designed to impart wisdom and guidance from the timeless teachings of the Bhagavad Gita. By leveraging modern AI, sentiment analysis, and the Google Cloud Translation API, GitaBot provides insightful responses to user queries, reflecting the teachings of Lord Krishna. This unique integration of spiritual guidance and technology offers users a profound and personalized experience. GitaBot supports both English and Hindi, making the teachings accessible to a wider audience.

## Features
- **Interactive Chatbot**: Engage in meaningful conversations and receive responses rooted in the Bhagavad Gita's wisdom.
- **Sentiment Analysis**: Analyze the emotional tone of your queries and view sentiment scores in percentages using VADER (Valence Aware Dictionary and sEntiment Reasoner) from NLTK.
- **Sentiment-Based Guidance**: Experience tailored responses that adapt to the sentiment of your queries. GitaBot offers context-aware advice based on whether your query is Positive, Negative, or Neutral.
- **Multilingual Support**: Interact with GitaBot in English or Hindi. Queries and responses can be translated between languages using the Google Cloud Translation API.
- **Groq-Powered Responses**: Responses are generated using the Groq API with the `openai/gpt-oss-120b` model.
- **Visually Appealing Interface**: Enjoy a user-friendly and visually captivating interface built with HTML, CSS, Bootstrap, and JavaScript (Flask-based web interface).

## Installation
To utilize GitaBot locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Manshi-Rathour/GitaBot
   # or
   git clone https://github.com/sSumankumari/GitaBot
   ```

2. **Navigate to the project directory**:
   ```bash
   cd GitaBot
   ```

3. **Set Up a Virtual Environment**:
   Create and activate a virtual environment for dependency management:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   Install the necessary packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure API Keys**:
   Set up your API keys in a `.env` file. Create a `.env` file in the root directory and add the following line:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *Note: For Hindi translation, GitaBot also uses Google Cloud Translation API. Ensure the credentials file is placed in the project root and referenced in `app.py`.*

6. **Run the Application**:
   To run the Flask app, use the following command:
   ```bash
   python app.py
   ```

## Prompt Examples

### Personal Guidance and Inner Peace
- "I feel anxious about my future. What should I do?"
- "How can I find inner peace?"
- "What does the Bhagavad Gita say about handling stress?"
- "How can I find inner peace according to the Bhagavad Gita?"
- "How do I maintain a positive attitude during tough times?"

### Teachings and Concepts of the Bhagavad Gita
- "What is the main message of the Bhagavad Gita?"
- "Can you explain the concept of Dharma in the Bhagavad Gita?"
- "What is Karma Yoga?"
- "How can I apply the teachings of the Bhagavad Gita to modern life?"
- "How does the Bhagavad Gita address the concept of attachment?"

### Moral and Philosophical Inquiries
- "What is the significance of karma according to the Gita?"
- "How can I apply the teachings of the Bhagavad Gita to modern life?"
- "What is the significance of meditation in the Bhagavad Gita?"
- "Can you explain the role of a teacher in the Bhagavad Gita?"
- "How does the Bhagavad Gita address the concept of attachment?"

## Contributors
- **Manshi Rathour** - <a href="https://github.com/Manshi-Rathour" target="_blank">GitHub Profile</a>
- **Sumankumari** - <a href="https://github.com/sSumankumari" target="_blank">GitHub Profile</a>

## Acknowledgements
Thank you for choosing GitaBot! We hope you find clarity and wisdom through our application. Your journey towards spiritual and mental well-being is our priority.

## Preview
- <a href="https://bit.ly/gita-bot" target="_blank">GitaBot</a>