@echo off
echo ========================================
echo  Final fix and push to GitHub
echo ========================================
cd /d "c:\Users\hp\Documents\NexeAgent_internship"

echo Clearing git lock...
del /f .git\index.lock 2>nul

echo Renaming Multi-Agent-System to 06-Multi-Agent-System...
if exist "Multi-Agent-System" rename "Multi-Agent-System" "06-Multi-Agent-System"

echo Staging all changes...
git add -A

echo Committing...
git commit -m "refactor: rename to 01-06 prefixes + add streamlit_app.py for all projects"

echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo  DONE! Now use these paths in Streamlit Cloud:
echo.
echo  Project 1: 01-Tool-Calling-AI-Agent/streamlit_app.py
echo  Project 2: 02-AI-Calculator-Agent/streamlit_app.py
echo  Project 3: 03-Multi-Tool-Agent/streamlit_app.py
echo  Project 4: 04-RAG-Assistant/streamlit_app.py
echo  Project 5: 05-Autonomous-Business-Agent/streamlit_app.py
echo  Project 6: 06-Multi-Agent-System/streamlit_app.py
echo ========================================
pause
