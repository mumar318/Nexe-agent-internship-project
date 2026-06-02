# config.py — unified config loader
# Reads from Streamlit secrets (when deployed) or .env (local).

import os
from dotenv import load_dotenv

load_dotenv()


def get(key: str, default: str = "") -> str:
    """
    Returns config value. Priority:
    1. Streamlit secrets (st.secrets) — available on Streamlit Cloud
    2. Environment variable / .env
    3. default
    """
    try:
        import streamlit as st
        val = st.secrets.get(key, None)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)
