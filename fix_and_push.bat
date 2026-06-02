@echo off
echo ========================================
echo  NexeAgent - Fix folder names and push
echo ========================================

cd /d "c:\Users\hp\Documents\NexeAgent_internship"

echo Deleting git lock...
del /f .git\index.lock 2>nul

echo Renaming Multi-Agent-System folder...
rename "Multi-Agent-System" "06-Multi-Agent-System"

echo Staging all changes...
git add -A

echo Committing...
git commit -m "refactor: rename all project folders with numbered prefixes (01-06)"

echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo  DONE! Check github.com/mumar318
echo ========================================
pause
