# app.py

import streamlit as st
import requests
import os

st.title("🤖 AI Tool Calling Agent")

# Railway pe API URL environment variable se lein, local pe localhost use karein
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# User input box
user_input = st.text_input("Enter your query:")

# Button click
if st.button("Run"):
    if not user_input.strip():
        st.warning("Please enter a query!")
    else:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"query": user_input},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Show result in user-friendly way
            if "result" in data:
                st.success("✅ Result:")
                st.write(data["result"])
            elif "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.json(data)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Make sure FastAPI is running!")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.write(e.response.text)