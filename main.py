import streamlit as st
from helper import chatbot_response


def main():
    st.markdown("# **Discover Wisdom with Lord Krishna**")

    query = st.text_area("Ask your query:")

    if st.button("Get Response"):
        if query:
            response_data = chatbot_response(query)
            st.subheader("Lord Krishna's Response:")

            formatted_response = response_data["Response"].replace("\n", "\n\n")

            st.write(formatted_response)


if __name__ == "__main__":
    main()
