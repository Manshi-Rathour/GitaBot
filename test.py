import os
import pandas as pd
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import re

# Load environment variables
load_dotenv()

# Load your dataset
data = pd.read_csv('Bhagwad_Gita.csv')

# Load API key from environment variables
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY not found in environment variables.")

# Initialize Google Generative AI with the provided API key
llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=api_key, temperature=0.2)

# Define prompt templates
prompt_template_with_id = """
Using the wisdom of the Bhagavad Gita, respond to the following query as if Lord Krishna himself is addressing the person:
Query: {query}
Response:
Please start your response with the ID of the most relevant shloka in the exact format BGX.Y, followed by your response.
For example, "BG2.47: You have the right to perform your prescribed duties, but you are not entitled to the fruits of your actions."
Only provide one shloka ID and a concise response.
"""

prompt_template_general = """
Imagine Lord Krishna personally addressing you, imparting his timeless wisdom from the Bhagavad Gita to help solve your problem:

Query: "{query}"

My dear child, I understand your concern. In the Bhagavad Gita, I teach that {query}. This principle is fundamental to finding inner peace and {query}. Reflect on this teaching and {query}. This approach will guide you towards spiritual and mental well-being. Remember, you are not alone on this journey. Meditate on these teachings and {query}. May you find clarity and peace.

Think of me as your guide on this path, offering wisdom to illuminate your way forward.
"""

prompt_with_id = PromptTemplate(input_variables=["query"], template=prompt_template_with_id)
prompt_general = PromptTemplate(input_variables=["query"], template=prompt_template_general)

# Create the LangChain instances with Google Generative AI
chain_with_id = LLMChain(llm=llm, prompt=prompt_with_id)
chain_general = LLMChain(llm=llm, prompt=prompt_general)


def generate_response(query, use_dataset=True):
    if use_dataset:
        # Generate response with Shloka ID
        response = chain_with_id.run(query)

        # Extract the first valid ID from response using regular expression
        id_pattern = r'BG\d+\.\d+'
        matches = re.findall(id_pattern, response)
        if matches:
            id_mentioned = matches[0]
            # Ensure ID exists in the dataset
            if id_mentioned in data['ID'].values:
                # Retrieve corresponding Shloka, HinMeaning, and EngMeaning
                selected_row = data[data['ID'] == id_mentioned].iloc[0]
                shloka = selected_row['Shloka']
                hin_meaning = selected_row['HinMeaning']
                eng_meaning = selected_row['EngMeaning']

                result = {
                    "response": response,
                    "id": id_mentioned
                }

                if pd.notna(shloka):
                    result["shloka"] = shloka
                if pd.notna(hin_meaning):
                    result["hin_meaning"] = hin_meaning
                if pd.notna(eng_meaning):
                    result["eng_meaning"] = eng_meaning

                return result
            else:
                # If ID is not in dataset, provide a general response
                return generate_general_response(query)
        else:
            # Handle case where no valid ID is found
            return generate_general_response(query)
    else:
        # Generate general response without dataset validation
        return generate_general_response(query)


def generate_general_response(query):
    # Generate general response
    response = chain_general.run(query)
    return {
        "response": response
    }


# Example usage
query = "How can I find inner peace?"

# Generate response with dataset
result_with_dataset = generate_response(query, use_dataset=True)
print("With Dataset:")
print(result_with_dataset)

# Generate response without dataset
result_without_dataset = generate_response(query, use_dataset=False)
print("\nWithout Dataset:")
print(result_without_dataset)
