# run.py — starts FastAPI and Streamlit together

import subprocess
import sys

fastapi = subprocess.Popen(
    ["uvicorn", "api:app", "--reload", "--host", "127.0.0.1", "--port", "8006"]
)

streamlit = subprocess.Popen(
    ["streamlit", "run", "app.py", "--server.port", "8507"]
)

try:
    fastapi.wait()
    streamlit.wait()
except KeyboardInterrupt:
    fastapi.terminate()
    streamlit.terminate()
    sys.exit(0)
