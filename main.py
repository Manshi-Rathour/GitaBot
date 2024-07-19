import streamlit as st
from helper import chatbot_response, analyze_sentiment_vader


def main():
    # Set the page configuration
    st.set_page_config(
        page_title="Bhagavad Gita Chatbot",
        page_icon=":om:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Adding a background image
    page_bg_img = '''
    <style>
    body {
    background-image: url("img/bg.png");
    background-size: cover;
    color: white;
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
        margin: auto;
        width: 50%;
        text-align: center;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Title and description
    st.markdown("<h1 style='text-align: center; color: gold;'>Discover Wisdom with Lord Krishna</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: white;'>Seek guidance from the timeless teachings of the Bhagavad Gita</p>",
        unsafe_allow_html=True)

    # Input query area
    st.markdown("<h3 style='color: white;'>Ask your query:</h3>", unsafe_allow_html=True)
    query = st.text_area("Query", placeholder="Enter your question here...", label_visibility="collapsed")

    # Button to get response
    if st.button("Get Response"):
        if query:
            # Perform sentiment analysis
            sentiment_response, compound, neg, neu, pos, sentiment_message = analyze_sentiment_vader(query)

            # Display sentiment analysis
            sentiment_box = f"""
            <div class="sentiment-box">
                <h4 style='color: gold;'>Sentiment Analysis</h4>
                <p>Compound: {compound:.2f}%</p>
                <p>Negative: {neg:.2f}%</p>
                <p>Neutral: {neu:.2f}%</p>
                <p>Positive: {pos:.2f}%</p>
                <p>{sentiment_message}</p>
            </div>
            """
            st.markdown(sentiment_box, unsafe_allow_html=True)

            # Generate chatbot response
            response_data = chatbot_response(query)
            formatted_response = response_data["Response"].replace("\n", "\n\n")
            st.markdown("<h3 style='color: white;'>Response:</h3>", unsafe_allow_html=True)
            st.write(formatted_response)


if __name__ == "__main__":
    main()
