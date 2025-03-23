import requests
import chromadb
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import SysConfig

chroma_client = chromadb.PersistentClient(path="./medical_db")
collection = chroma_client.get_or_create_collection("blood_analysis")

if collection.count() == 0:
    collection.add(
        ids=["1"],
        documents=["A normal hemoglobin range for men is 13.8 to 17.2 g/dL, and for women is 12.1 to 15.1 g/dL."],
    )
    collection.add(
        ids=["2"],
        documents=["TSH (Thyroid-Stimulating Hormone) levels above 4.0 mIU/L may indicate hypothyroidism."],
    )

OLLAMA_URL = SysConfig.OLLAMA_URL
MODEL_NAME = "biomistral"

def ask_ollama(prompt, context=""):
    """Send a prompt to Ollama with optional context from ChromaDB."""
    full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False  
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code} - {response.text}"

if __name__ == "__main__":
    while True:
        user_input = input("\nAsk something (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        results = collection.query(query_texts=[user_input], n_results=1)

        context = results["documents"][0][0] if results["documents"] else "No relevant medical data found."

        response = ask_ollama(user_input, context)
        
        print(response)