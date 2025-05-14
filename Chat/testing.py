from llama_cpp import Llama
import chromadb

llm = Llama.from_pretrained(
    repo_id="ioana-manghiuc/bio-mistral-for-web",
    filename="ggml-model-Q5_K_M.gguf"
)

chroma_client = chromadb.PersistentClient(path="./medical_db")
collection = chroma_client.get_or_create_collection("blood_analysis")

def retrieve_context(query: str, n_results: int = 1) -> str:
    results = collection.query(query_texts=[query], n_results=n_results)
    documents = results["documents"][0] if results["documents"] else []
    return "\n".join(documents) if documents else "No relevant context found."


def rag_response(prompt: str) -> str:
    context = retrieve_context(prompt)
    full_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}\n\nAnswer:"
    output = llm(full_prompt, max_tokens=512)
    return output['choices'][0]['text'].strip()


if __name__ == "__main__":
    while True:
        user_input = input("\nAsk something (or type 'exit'): ")
        if user_input.lower() == "exit":
            break
        answer = rag_response(user_input)
        print("\nResponse:\n", answer)