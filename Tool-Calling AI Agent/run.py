import subprocess

# Start FastAPI
fastapi = subprocess.Popen(["uvicorn", "api:app", "--reload"])

# Start Streamlit
streamlit = subprocess.Popen(["streamlit", "run", "app.py"])

# Keep both running
fastapi.wait()
streamlit.wait()