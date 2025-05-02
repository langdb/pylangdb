import pandas as pd
from pylangdb import LangDb
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("LANGDB_API_KEY")

# Read CSV
df = pd.read_csv("sample.csv")
data = df.to_dict(orient='records')

question = "Analyze the engagement data of company's  LinkedIn page for April month. What are the key insights and trends? Suggestions to improve the engagement rate?"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f'Analyze this CSV file data: {data} and nswer the question: {question}'},
]
# Call Gemini Model using LangDB
client = LangDb(api_key=API_KEY)
response = client.completion(
    model="gemini-1.5-pro-latest",
    messages=messages,
    temperature=0.7,
    # max_tokens=1000,
)

print(response['content'])
