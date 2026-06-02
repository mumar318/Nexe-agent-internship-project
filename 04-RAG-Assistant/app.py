# app.py

import streamlit as st
import requests
import os

st.set_page_config(
    page_title="RAG Assistant",
    page_icon="📚",
    layout="centered"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8003")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📚 RAG Assistant")
st.caption("Upload documents · Ask questions · Get contextual answers powered by Groq LLaMA")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Ask", "📂 Upload", "🗂️ Documents"])

# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: Ask a Question
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Ask a question about your documents")

    with st.expander("💡 Example questions"):
        st.markdown("""
- `What is the main topic of the document?`
- `Summarize the key points`
- `What does the document say about [topic]?`
- `List the main conclusions`
""")

    question = st.text_area(
        "Your question:",
        placeholder="e.g. What are the key findings in the document?",
        height=100
    )
    ask_btn = st.button("Ask", type="primary", use_container_width=True)

    if ask_btn:
        if not question.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            with st.spinner("Searching documents and generating answer..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question},
                        timeout=60
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    st.divider()

                    # Answer
                    st.success("💡 Answer")
                    st.markdown(data.get("answer", "No answer returned."))

                    # Sources
                    sources = data.get("sources", [])
                    if sources:
                        st.info(f"📄 Sources: {', '.join(sources)}")

                    # Context expandable
                    context = data.get("context_used", "")
                    if context:
                        with st.expander("🔍 Context used from documents"):
                            st.text(context)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure FastAPI is running on port 8003.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: Upload Document
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Upload a document to the knowledge base")
    st.caption("Supported formats: PDF, TXT, MD")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "md"],
        help="Upload a PDF or text file to add to the knowledge base"
    )

    upload_btn = st.button("Upload & Index", type="primary", use_container_width=True)

    if upload_btn:
        if uploaded_file is None:
            st.warning("⚠️ Please select a file first.")
        else:
            with st.spinner(f"Uploading and indexing '{uploaded_file.name}'..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=120
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    st.success(data.get("message", "Upload successful!"))
                    st.metric("Chunks indexed", data.get("chunks_stored", 0))

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure FastAPI is running on port 8003.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Upload failed: {e.response.text}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: Manage Documents
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Documents in knowledge base")

    col1, col2 = st.columns([3, 1])
    with col2:
        refresh = st.button("🔄 Refresh", use_container_width=True)

    try:
        resp = requests.get(f"{API_URL}/documents", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        docs = data.get("documents", [])

        if not docs:
            st.info("No documents uploaded yet. Go to the Upload tab to add documents.")
        else:
            st.caption(f"{len(docs)} document(s) in knowledge base")
            for doc in docs:
                col_name, col_del = st.columns([4, 1])
                with col_name:
                    st.markdown(f"📄 **{doc}**")
                with col_del:
                    if st.button("🗑️", key=f"del_{doc}", help=f"Delete {doc}"):
                        try:
                            del_resp = requests.delete(
                                f"{API_URL}/documents/{doc}",
                                timeout=15
                            )
                            del_resp.raise_for_status()
                            st.success(f"Deleted '{doc}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {e}")

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure FastAPI is running on port 8003.")
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
