from openai import OpenAI
from dotenv import load_dotenv
import os 
import numpy
load_dotenv()
client=OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY") 
)

def get_embedding(text):
    response = client.embeddings.create(
        model="nomic-embed-text",
        input=text
    )
    return response.data[0].embedding

def cosine_sim(A,B):
    dot_prod=numpy.dot(A,B)
    norm_a=numpy.linalg.norm(A)
    norm_b=numpy.linalg.norm(B)
    return dot_prod/(norm_a*norm_b)