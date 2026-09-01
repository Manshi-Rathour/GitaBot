import os
import re
import pandas as pd
from dotenv import load_dotenv
import groq

load_dotenv()


try:
    data = pd.read_csv('Bhagwad_Gita.csv')
except FileNotFoundError:
    raise Exception("Dataset 'Bhagwad_Gita.csv' not found. Ensure the file is in the correct directory.")


api_key = os.getenv('GROQ_API_KEY')
if api_key is None:
    raise Exception("Groq API key not found. Ensure the API key is set in your environment variables.")


groq_client = groq.Client(api_key=api_key)

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
Imagine Lord Krishna personally addressing you, imparting his timeless wisdom from the Bhagavad Gita to help address your concern:

Query: "{query}"

My dear child, I understand your concern about "{query}". The Bhagavad Gita teaches us valuable lessons that can guide us in such situations. Remember, think of me as your guide, offering wisdom to illuminate your way forward.

May you find clarity and peace as you reflect on these teachings and navigate your journey.

IMPORTANT FORMATTING RULE: Whenever you refer to a specific verse, never use the internal
shorthand code format (e.g. "BG2.47", "BG 6.9", "(BG2.47)"). That code is not meant for the
reader. Instead, always write it out in plain words as "Chapter X, Verse Y" (e.g.
"Chapter 2, Verse 47"). Do not use the abbreviation "BG" anywhere in your response.
"""


def generate_groq_response(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error communicating with Groq API: {e}")


# Safety net: even with the prompt instruction above, LLMs occasionally slip
# back into the raw "BGX.Y" citation style. This catches any leftover
# occurrences and rewrites them into plain, translatable English before the
# text ever reaches the translation step or the user.
_BG_CODE_RE = re.compile(r'\(?\s*BG\s*[-\.]?\s*(\d+)\.(\d+)\s*\)?', re.IGNORECASE)
_GITA_CODE_RE = re.compile(r'Bhagavad[\s-]?Gita\s+(\d+)\.(\d+)', re.IGNORECASE)


def humanize_verse_citations(text):
    """Replace any raw 'BGX.Y' / 'Bhagavad Gita X.Y' style citation in
    user-facing text with a plain 'Chapter X, Verse Y' phrase, so it reads
    naturally in English and translates cleanly into Hindi (avoids Google
    Translate transliterating 'BG' into 'बीजी')."""
    if not text:
        return text

    text = _BG_CODE_RE.sub(lambda m: f"Chapter {m.group(1)}, Verse {m.group(2)}", text)
    text = _GITA_CODE_RE.sub(lambda m: f"Bhagavad Gita, Chapter {m.group(1)}, Verse {m.group(2)}", text)
    return text


def generate_response(query, use_dataset=True):
    # Generate general response
    general_response = generate_groq_response(prompt_template_general.format(query=query))
    general_response = humanize_verse_citations(general_response)

    if use_dataset:
        # Generate response with Shloka ID (this one is for internal lookup
        # only — its raw "BGX.Y" format is never shown to the user directly)
        dataset_response = generate_groq_response(prompt_template_with_id.format(query=query))

        # Extract the first valid ID from response using regular expression
        id_pattern = r'BG\d+\.\d+'
        matches = re.findall(id_pattern, dataset_response)
        if matches:
            id_mentioned = matches[0]
            # Ensure ID exists in the dataset
            if id_mentioned in data['ID'].values:
                # Retrieve corresponding Shloka, HinMeaning, and EngMeaning
                selected_row = data[data['ID'] == id_mentioned].iloc[0]
                shloka = selected_row['Shloka']
                hin_meaning = selected_row['HinMeaning']
                eng_meaning = selected_row['EngMeaning']
                chapter = id_mentioned.split('.')[0][2:]  # Extract chapter
                verse = id_mentioned.split('.')[1]  # Extract verse

                result = {
                    "general_response": general_response,
                    "dataset_response": f"Chapter: {chapter} and Shloka: {verse}",
                    "id": id_mentioned,
                    "shloka": shloka,
                    "hin_meaning": hin_meaning,
                    "eng_meaning": eng_meaning
                }

                return result
            else:
                return {
                    "general_response": general_response,
                    "dataset_response": "",
                    "id": "",
                    "shloka": "",
                    "hin_meaning": "",
                    "eng_meaning": ""
                }
        else:
            return {
                "general_response": general_response,
                "dataset_response": "",
                "id": "",
                "shloka": "",
                "hin_meaning": "",
                "eng_meaning": ""
            }
    else:
        return {
            "general_response": general_response,
            "dataset_response": "",
            "id": "",
            "shloka": "",
            "hin_meaning": "",
            "eng_meaning": ""
        }


if __name__ == "__main__":
    query = "How can I find inner peace?"
    result = generate_response(query)
    print(result)