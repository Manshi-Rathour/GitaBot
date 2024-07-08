from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os


load_dotenv()

# Load API key from environment variables
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY not found in environment variables.")

# Initialize Google Generative AI with the provided API key
llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=api_key, temperature=0.2)

# Prompt Template for generating responses
prompt_template = """
Imagine Lord Krishna personally addressing you, imparting his timeless wisdom from the Bhagavad Gita to help solve your problem:

Query: "{input}"

My dear child, I understand your concern. In the Bhagavad Gita, I teach that {input}. This principle is fundamental to finding inner peace and {input}. Reflect on this teaching and {input}. This approach will guide you towards spiritual and mental well-being. Remember, you are not alone on this journey. Meditate on these teachings and {input}. May you find clarity and peace.

Think of me as your guide on this path, offering wisdom to illuminate your way forward.
"""

prompt = PromptTemplate(input_variables=["input"], template=prompt_template)

# Create the LangChain instance with Google Generative AI
chain = LLMChain(llm=llm, prompt=prompt)


def chatbot_response(query):
    try:
        response = chain.run(input=query, max_tokens=100)
        formatted_response = response.replace("\\n", "\n").replace("\n\n", "\n").strip()
        return {"Response": formatted_response}
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return {"Response": "Sorry, I can't answer this query!"}


if __name__ == "__main__":
    query = "How can I overcome feelings of anger?"
    response_data = chatbot_response(query)
    print(response_data["Response"].replace("\n", "\n\n"))
