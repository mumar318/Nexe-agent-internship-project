# streamlit_app.py — Streamlit Cloud entry point for RAG Assistant
# Runs RAG logic directly — no FastAPI server needed.

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Assistant", page_icon="📚", layout="centered")
st.title("📚 RAG Assistant")
st.caption("Upload documents · Ask questions · Get grounded answers — powered by Groq LLaMA")
st.divider()

def _get(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

# Set GROQ key before importing modules that use it
os.environ.setdefault("GROQ_API_KEY", _get("GROQ_API_KEY"))

tab1, tab2, tab3 = st.tabs(["💬 Ask", "📂 Upload", "🗂️ Documents"])

# ── Tab 1: Ask ─────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Ask a question about your documents")
    with st.expander("💡 Example questions"):
        st.markdown("""
- `What is the main topic of the document?`
- `Summarize the key points`
- `What does the document say about machine learning?`
""")
    question = st.text_area("Your question:", placeholder="e.g. What are the key findings?", height=100)
    ask_btn  = st.button("Ask", type="primary", use_container_width=True)

    if ask_btn:
        if not question.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            with st.spinner("Searching documents and generating answer..."):
                try:
                    from rag_chain import answer_question
                    data = answer_question(question)
                    st.divider()
                    st.success("💡 Answer")
                    st.markdown(data.get("answer", "No answer returned."))
                    sources = data.get("sources", [])
                    if sources:
                        st.info(f"📄 Sources: {', '.join(sources)}")
                    ctx = data.get("context_used", "")
                    if ctx:
                        with st.expander("🔍 Context used"):
                            st.text(ctx[:2000])
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.info("Make sure you've uploaded at least one document first.")

# ── Tab 2: Upload ──────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Upload a document to the knowledge base")
    st.caption("Supported: PDF, TXT, MD")
    uploaded = st.file_uploader("Choose a file", type=["pdf", "txt", "md"])
    up_btn   = st.button("Upload & Index", type="primary", use_container_width=True)

    if up_btn:
        if uploaded is None:
            st.warning("⚠️ Please select a file first.")
        else:
            with st.spinner(f"Indexing '{uploaded.name}'..."):
                try:
                    import tempfile, pathlib
                    from vector_store import ingest_document
                    os.makedirs("uploaded_docs", exist_ok=True)
                    save_path = os.path.join("uploaded_docs", uploaded.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    chunks = ingest_document(save_path, uploaded.name)
                    st.success(f"✅ '{uploaded.name}' indexed successfully!")
                    st.metric("Chunks stored", chunks)
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

# ── Tab 3: Documents ───────────────────────────────────────────────────────────
with tab3:
    st.subheader("Documents in knowledge base")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    try:
        from vector_store import list_documents, delete_document
        docs = list_documents()
        if not docs:
            st.info("No documents uploaded yet.")
        else:
            st.caption(f"{len(docs)} document(s) in knowledge base")
            for doc in docs:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"📄 **{doc}**")
                with col2:
                    if st.button("🗑️", key=f"del_{doc}"):
                        delete_document(doc)
                        st.success(f"Deleted '{doc}'")
                        st.rerun()
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
