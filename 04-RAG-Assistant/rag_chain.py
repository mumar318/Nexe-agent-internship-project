# rag_chain.py
# Retrieves relevant context from ChromaDB and generates answers via Groq LLaMA

import os
from dotenv import load_dotenv
from groq import Groq
from vector_store import similarity_search

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based strictly on the provided context.

RULES:
- Only use information from the context below to answer
- If the answer is not in the context, say: "I couldn't find relevant information in the uploaded documents."
- Be concise and accurate
- Cite the source document when possible
"""


def answer_question(query: str, k: int = 4) -> dict:
    """
    Retrieve relevant chunks from vector store and generate a contextual answer.
    """
    try:
        docs = similarity_search(query, k=k)

        if not docs:
            return {
                "answer": "No documents found in the knowledge base. Please upload a document first.",
                "sources": [],
                "context_used": ""
            }

        # Build context and collect sources
        context_parts = [doc["content"] for doc in docs]
        sources = list(set(doc["source"] for doc in docs))
        context = "\n\n---\n\n".join(context_parts)

        user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Answer based only on the context above:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()

        return {
            "answer": answer,
            "sources": sorted(sources),
            "context_used": context
        }

    except Exception as e:
        return {
            "answer": f"❌ Error generating answer: {str(e)}",
            "sources": [],
            "context_used": ""
        }
