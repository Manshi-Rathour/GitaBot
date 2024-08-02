import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from helper import chatbot_response, analyze_sentiment_vader

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
        st.markdown("<h1 style='text-align: center; color: gold;'>Discover Wisdom with Lord Krishna</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white;'>Seek guidance from the timeless teachings of the Bhagavad Gita</p>", unsafe_allow_html=True)

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
                    sentiment_response, compound, neg, neu, pos, sentiment_message = analyze_sentiment_vader(query)

                    # Generate chatbot response
                    response_data = chatbot_response(query)
                    formatted_response = response_data["Response"].replace("\n", "\n\n")

                    # Remove asterisks from the response
                    formatted_response = formatted_response.replace("**", "")

                    # Store results in session state
                    st.session_state['query'] = query
                    st.session_state['response'] = formatted_response
                    st.session_state['sentiment'] = {
                        'compound': compound,
                        'neg': neg,
                        'neu': neu,
                        'pos': pos,
                        'message': sentiment_message
                    }
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        # Display the response if available
        if 'response' in st.session_state:
            query = st.session_state.get('query', '')
            formatted_response = st.session_state.get('response', '')
            sentiment = st.session_state.get('sentiment', {})

            # Display sentiment analysis and response in columns
            col1, col2 = st.columns([7, 3])

            with col1:
                st.markdown("<p class='subtitle'>Guidance Based on Your Query</p>", unsafe_allow_html=True)
                response_container = f"""
                <div class="formated-response-container">
                    <p>{formatted_response}</p>
                </div>
                """
                st.markdown(response_container, unsafe_allow_html=True)

            with col2:
                sentiment_box = f"""
                <div class="sentiment-box">
                    <h3 style='color: gold;'>Sentiment Evaluation</h3>
                    <h4 class="subtitle" style=' text-align: center'>Understanding the Emotional Tone</h4>
                    <p>Compound: {sentiment.get('compound', 0):.2f}</p>
                    <p>Negative: {sentiment.get('neg', 0):.2f}</p>
                    <p>Neutral: {sentiment.get('neu', 0):.2f}</p>
                    <p>Positive: {sentiment.get('pos', 0):.2f}</p>
                    <p>{sentiment.get('message', '')}</p>
                </div>
                """
                st.markdown(sentiment_box, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
