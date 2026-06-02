@echo off
cd /d "c:\Users\hp\Documents\NexeAgent_internship"

del /f .git\index.lock 2>nul
echo Lock cleared.

git add 01-Tool-Calling-AI-Agent/streamlit_app.py
git add 02-AI-Calculator-Agent/streamlit_app.py
git add 03-Multi-Tool-Agent/streamlit_app.py
git add 04-RAG-Assistant/streamlit_app.py
git add 05-Autonomous-Business-Agent/streamlit_app.py
git add Multi-Agent-System/streamlit_app.py

git commit -m "feat: add streamlit_app.py for all 6 projects (Streamlit Cloud deployment)"
git push origin main

echo.
echo DONE. All projects ready for Streamlit Cloud.
pause
