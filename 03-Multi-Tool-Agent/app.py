# app.py — works on Streamlit Cloud (direct agent call, no FastAPI needed)

import streamlit as st
import os, json, re, sqlite3, smtplib
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Multi-Tool Agent", page_icon="🤖", layout="centered")
st.title("🤖 Multi-Tool Agent")
st.caption("Web Search · Save Notes · Send Email — powered by Groq LLaMA")
st.divider()

def _get(key):
    try: return st.secrets[key]
    except Exception: return os.getenv(key, "")

def web_search(query):
    import requests as r
    key = _get("SERPAPI_KEY")
    if not key: return "❌ SERPAPI_KEY not set in secrets."
    try:
        data = r.get("https://serpapi.com/search",
                     params={"q":query,"api_key":key,"num":3,"engine":"google"},timeout=15).json()
        if "error" in data: return f"❌ {data['error']}"
        results = data.get("organic_results",[])
        if not results: return "⚠️ No results found."
        out = f"🔍 Results for '{query}':\n\n"
        for i,r2 in enumerate(results[:3],1):
            out += f"{i}. **{r2.get('title','')}**\n   {r2.get('snippet','')}\n   🔗 {r2.get('link','')}\n\n"
        return out.strip()
    except Exception as e: return f"❌ Search failed: {e}"

def save_note(title, content):
    try:
        conn = sqlite3.connect("notes.db")
        conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, timestamp TEXT)")
        conn.execute("INSERT INTO notes VALUES (NULL,?,?,?)",(title,content,datetime.utcnow().isoformat()))
        conn.commit(); conn.close()
        return f"✅ Note saved!\n📌 {title}\n📝 {content}"
    except Exception as e: return f"❌ {e}"

def send_email(to, subject, body):
    addr=_get("EMAIL_ADDRESS"); pwd=_get("EMAIL_PASSWORD")
    if not addr or not pwd: return "❌ EMAIL_ADDRESS or EMAIL_PASSWORD not set."
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg=MIMEMultipart(); msg["From"]=addr; msg["To"]=to; msg["Subject"]=subject
        msg.attach(MIMEText(body,"plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(addr,pwd); s.sendmail(addr,to,msg.as_string())
        return f"✅ Email sent to {to}"
    except smtplib.SMTPAuthenticationError: return "❌ Gmail auth failed."
    except Exception as e: return f"❌ {e}"

TOOL_MAP = {"web_search":web_search,"save_note":save_note,"send_email":send_email}

tab1, tab2 = st.tabs(["💬 Chat","📋 Saved Notes"])

with tab1:
    with st.expander("💡 Example queries"):
        st.markdown("""
- `Search for latest AI news`
- `Save a note titled Ideas with content: Build a chatbot`
- `Send an email to someone@gmail.com about the meeting`
""")
    user_input = st.text_input("Enter your query:")
    run_btn = st.button("Run", type="primary", use_container_width=True)

    if run_btn:
        if not user_input.strip():
            st.warning("⚠️ Please enter a query.")
        else:
            with st.spinner("Working..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=_get("GROQ_API_KEY"))
                    SYSTEM = """You are a strict tool-calling AI. ONLY return JSON. NO markdown.
TOOLS: web_search(query) save_note(title,content) send_email(to,subject,body)
FORMAT: {"name":"tool_name","arguments":{"param":"value"}}"""
                    resp    = client.chat.completions.create(model="llama-3.1-8b-instant",
                        messages=[{"role":"system","content":SYSTEM},{"role":"user","content":user_input}])
                    message = resp.choices[0].message.content.strip()
                    cleaned = re.sub(r"```(?:json)?","",message,flags=re.IGNORECASE).replace("```","").strip()
                    data    = json.loads(cleaned)
                    tool    = data.get("name",""); args = data.get("arguments",{})
                    if tool not in TOOL_MAP:
                        st.error(f"❌ Unknown tool: {tool}")
                    else:
                        result = TOOL_MAP[tool](**args)
                        st.divider()
                        if tool=="web_search": st.success("🔍 Results"); st.markdown(result)
                        elif tool=="save_note": st.success("💾 Saved"); st.info(result)
                        elif tool=="send_email": st.success("📧 Email"); st.info(result)
                        with st.expander("🔍 Raw"): st.json({"tool":tool,"input":args,"result":result})
                except json.JSONDecodeError: st.error("❌ Could not parse LLM response.")
                except Exception as e: st.error(f"❌ {e}")

with tab2:
    st.subheader("📋 Saved Notes")
    if st.button("🔄 Refresh"): st.rerun()
    try:
        conn = sqlite3.connect("notes.db")
        conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, timestamp TEXT)")
        rows = conn.execute("SELECT id,title,content,timestamp FROM notes ORDER BY id DESC").fetchall()
        conn.close()
        if not rows: st.info("No notes yet.")
        else:
            for r in rows:
                with st.expander(f"📌 {r[1]}  —  {r[3][:19]}"): st.write(r[2])
    except Exception as e: st.error(f"❌ {e}")
