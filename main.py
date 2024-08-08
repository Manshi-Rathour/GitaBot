import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from helper import generate_response
from sentiment_helper import analyze_sentiment_vader, generate_learning_message
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_base64(file_path):
    """Encode image to Base64."""
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def set_background(png_file):
    """Set background image using Base64 encoding."""
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-repeat: repeat;
        background-attachment: fixed;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def main():
    # Load the custom icon and image
    feather_icon = Image.open("img/feather.png")
    bot_image = Image.open("img/bot_image.jpeg")
    bot_image = bot_image.resize((300, 300))
    bot_image_base64 = image_to_base64(bot_image)

    # Set the page configuration
    st.set_page_config(
        page_title="Bhagavad Gita Chatbot",
        page_icon=feather_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Set background image
    set_background('img/bg.png')  # Path to your background image

    # Adding other CSS styling for elements
    page_styles = '''
        <style>
        body {
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            flex-direction: column;
        }
        .stButton>button {
            background-color: gold;
            color: black;
        }
        .stTextArea textarea {
            background-color: black;
            color: white;
        }
        .sentiment-box {
            border: 2px solid gold;
            padding: 10px;
            border-radius: 10px;
            background-color: black;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: auto;
            width: 100%;
        }
        .subtitle {
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            text-align: center;
            border-bottom: 2px solid gold; 
            padding-bottom: 5px; 
        }
        .centered-image {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .formated-response-container {
            color: white;
        }
        </style>
        '''
    st.markdown(page_styles, unsafe_allow_html=True)

    # Main container
    with st.container():
        # Title and description
        st.markdown("<h1 style='text-align: center; color: gold;'>Discover Wisdom with Lord Krishna</h1>",
                    unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: white;'>Seek guidance from the timeless teachings of the Bhagavad Gita</p>",
            unsafe_allow_html=True)

        # Display the centered image using HTML
        image_html = f"""
        <div class='centered-image'>
            <img src='data:image/jpeg;base64,{bot_image_base64}' width='300' />
        </div>
        """
        st.markdown(image_html, unsafe_allow_html=True)

        # Input query area
        st.markdown("<h3 style='color: white;'>Ask your query:</h3>", unsafe_allow_html=True)
        query = st.text_area("Query", placeholder="Enter your question here...", label_visibility="collapsed")

        # Button to get response
        if st.button("Get Response"):
            if query:
                try:
                    # Perform sentiment analysis
                    sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(query)
                    learning_message = generate_learning_message(sentiment_message)

                    # Generate chatbot response
                    response_data = generate_response(query)

                    if response_data["general_response"] and response_data["dataset_response"]:
                        general_response = response_data["general_response"]
                        dataset_response = response_data["dataset_response"]
                        shloka_id = response_data["id"]
                        shloka = response_data["shloka"]
                        hin_meaning = response_data["hin_meaning"]
                        eng_meaning = response_data["eng_meaning"]

                        # Store results in session state
                        st.session_state['query'] = query
                        st.session_state['general_response'] = general_response
                        st.session_state['dataset_response'] = dataset_response
                        st.session_state['shloka_id'] = shloka_id
                        st.session_state['shloka'] = shloka
                        st.session_state['hin_meaning'] = hin_meaning
                        st.session_state['eng_meaning'] = eng_meaning
                        st.session_state['sentiment'] = {
                            'compound': compound,
                            'neg': neg,
                            'neu': neu,
                            'pos': pos,
                            'message': sentiment_message,
                            'short_message': short_message,
                            'learning_message': learning_message
                        }
                    else:
                        st.session_state['general_response'] = "Sorry, I can't answer this query."
                        st.session_state['dataset_response'] = ""
                        st.session_state['shloka_id'] = ""
                        st.session_state['shloka'] = ""
                        st.session_state['hin_meaning'] = ""
                        st.session_state['eng_meaning'] = ""
                        st.session_state['sentiment'] = {
                            'compound': 0,
                            'neg': 0,
                            'neu': 0,
                            'pos': 0,
                            'message': "N/A",
                            'short_message': "N/A",
                            'learning_message': "N/A"
                        }
                except Exception as e:
                    st.session_state['general_response'] = "Sorry, I can't answer this query."
                    st.session_state['dataset_response'] = ""
                    st.session_state['shloka_id'] = ""
                    st.session_state['shloka'] = ""
                    st.session_state['hin_meaning'] = ""
                    st.session_state['eng_meaning'] = ""
                    st.session_state['sentiment'] = {
                        'compound': 0,
                        'neg': 0,
                        'neu': 0,
                        'pos': 0,
                        'message': "N/A",
                        'short_message': "N/A",
                        'learning_message': "N/A"
                    }
                    # Clear the default error message
                    st.markdown("<p style='color: transparent;'>An error occurred: list index out of range</p>",
                                unsafe_allow_html=True)

        # Display the response if available
        if 'general_response' in st.session_state:
            general_response = st.session_state.get('general_response', '')
            dataset_response = st.session_state.get('dataset_response', '')
            shloka_id = st.session_state.get('shloka_id', '')
            shloka = st.session_state.get('shloka', '')
            hin_meaning = st.session_state.get('hin_meaning', '')
            eng_meaning = st.session_state.get('eng_meaning', '')
            sentiment = st.session_state.get('sentiment', {})

            # Two-column layout
            col1, col2 = st.columns([2, 1])

            # Left column for Response
            with col1:
                if general_response == "Sorry, I can't answer this query.":
                    st.markdown(f"<p class='formated-response-container'>{general_response}</p>",
                                unsafe_allow_html=True)
                else:
                    # Display the response
                    st.markdown("<p class='subtitle'>Guidance Based on Your Query</p>", unsafe_allow_html=True)
                    response_container = f"""
                    <div class="formated-response-container">
                        <p>{general_response}</p>
                    </div>
                    """
                    st.markdown(response_container, unsafe_allow_html=True)

                    # Display the response from bhagwad gita
                    st.markdown("<p class='subtitle'>From Bhagavad Gita</p>", unsafe_allow_html=True)

                    if dataset_response:
                        # Safe extraction of chapter and shloka number
                        chapter = ""
                        shloka_num = ""
                        if shloka_id:
                            parts = shloka_id.split('.')
                            if len(parts) == 2:
                                chapter = parts[0][2:]  # Extract chapter number
                                shloka_num = parts[1]  # Extract shloka number

                        detailed_response = f"""
                        <div class="formated-response-container">
                            <p>Chapter: {chapter}</p>
                            <p>Shloka: {shloka_num}</p>
                            <p>Shloka: {shloka}</p>
                            <p>Hindi Meaning: {hin_meaning}</p>
                            <p>English Meaning: {eng_meaning}</p>
                        </div>
                        """
                        st.markdown(detailed_response, unsafe_allow_html=True)
                    else:
                        st.markdown("<p class='formated-response-container'>Sorry, I can't answer this query.</p>",
                                    unsafe_allow_html=True)

            # Right column for Sentiment Analysis
            with col2:
                if sentiment and sentiment['message'] != "N/A":
                    sentiment_box = f"""
                    <div class="sentiment-box">
                        <h3 style='color: gold;'>Sentiment Evaluation</h3>
                        <h4 class="subtitle" style=' text-align: center'>Understanding the Emotional Tone</h4>
                        <p>Compound: {sentiment.get('compound', 0):.2f}</p>
                        <p>Negative: {sentiment.get('neg', 0):.2f}</p>
                        <p>Neutral: {sentiment.get('neu', 0):.2f}</p>
                        <p>Positive: {sentiment.get('pos', 0):.2f}</p>
                        <p><b>Sentiment Message: </b> {sentiment.get('message', '')}</p>
                        <p><b>Short Message: </b> {sentiment.get('short_message', '')}</p>
                        <p><b>Learning Message: </b> {sentiment.get('learning_message', '')}</p>                    
                 
                    </div>
                    """
                    st.markdown(sentiment_box, unsafe_allow_html=True)
                else:
                    # Clear the default error message
                    st.markdown("<p style='color: transparent;'>No sentiment data available.</p>",
                                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
