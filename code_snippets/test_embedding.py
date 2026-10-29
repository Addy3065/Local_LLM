from openai import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()
client=OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY") 
)

response = client.embeddings.create(
    model="nomic-embed-text",
    input="I am a good developer" # input can be a list of strings f
)

print(response.data[0].embedding)