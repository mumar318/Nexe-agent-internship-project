# vector_store.py
# Document ingestion and retrieval using ChromaDB with fast-embed embeddings

import os
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = "chroma_db"
UPLOAD_DIR = "uploaded_docs"
COLLECTION_NAME = "rag_documents"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Use ChromaDB's built-in ONNX embedding (no torch/TF needed)
_embedding_fn = None


def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = ONNXMiniLM_L6_V2()
    return _embedding_fn


def get_collection():
    """Get or create the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_fn()
    )
    return collection


def ingest_document(file_path: str, filename: str) -> int:
    """Load, chunk, embed and store a document. Returns chunk count."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF, TXT, or MD.")

    documents = loader.load()
    chunks = text_splitter.split_documents(documents)

    collection = get_collection()
    texts = [c.page_content for c in chunks]
    ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk": i} for i in range(len(chunks))]

    batch_size = 50
    for i in range(0, len(texts), batch_size):
        collection.add(
            documents=texts[i:i + batch_size],
            ids=ids[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )

    return len(chunks)


def similarity_search(query: str, k: int = 4) -> list:
    """Return top-k relevant chunks for a query."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(k, count)
    )

    docs = []
    if results and results["documents"]:
        for i, text in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            docs.append({"content": text, "source": meta.get("source", "Unknown")})
    return docs


def list_documents() -> list:
    """Return sorted list of unique document names in the store."""
    collection = get_collection()
    results = collection.get(include=["metadatas"])
    sources = {m["source"] for m in results.get("metadatas", []) if m and "source" in m}
    return sorted(sources)


def delete_document(filename: str) -> int:
    """Delete all chunks for a given document. Returns deleted count."""
    collection = get_collection()
    results = collection.get(include=["metadatas"])
    ids_to_delete = [
        results["ids"][i]
        for i, m in enumerate(results.get("metadatas", []))
        if m and m.get("source") == filename
    ]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)
