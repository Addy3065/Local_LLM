import os 
from openai import OpenAI
from dotenv import load_dotenv
import numpy 

load_dotenv()

client=OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
embed_model=os.getenv("EMBEDDING_MODEL")
kb_folder=os.getenv("KB_FOLDER")


# create embeddings
def get_embedding(text):
    response = client.embeddings.create(
        model="nomic-embed-text",
        input=text
    )
    return response.data[0].embedding
# cosine similarity 
def cosine_sim(A,B):
    dot_prod=numpy.dot(A,B)
    norm_a=numpy.linalg.norm(A)
    norm_b=numpy.linalg.norm(B)
    return dot_prod/(norm_a*norm_b)
#loading docs 
def load_documents(folder=kb_folder):
    documents=[]
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue

        path=os.path.join(folder,filename)
        with open(path,"r",encoding="UTF-8") as f:
            documents.append(
                {
                    "source":filename,
                    "text":f.read()
                }
            )
    return documents


# Adding Embedding in a document 
def add_embedding(documents):
    for document in documents:
        vector=get_embedding(document["text"])
        document["vector"]=vector

    return documents

def search(query, documents, top_k=3):
    query_vector = get_embedding(query)

    results = []
    for document in documents:
        score = cosine_sim(query_vector, document["vector"])
        results.append(
            {
                "score" : float(score),
                "source": document["source"],
                "text": document["text"],
                "size": len(document["text"])
            }
        )

    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]

#testing method 
def test(user_query, documents, top_k=3):
    print(f"\nUser Query: {user_query}\n")

    results = search(user_query, documents, top_k)

    for r in results:
        print(f" {r['score']:.2f} - {r['source']} - {r['size']} characters)")
    
    

#Let's start testing
documents = load_documents()
documents = add_embedding(documents)

print(f"We have embedded {len(documents)} documents")

user_query = "How many days I will get for maternity leave ?"
test(user_query, documents, 3)