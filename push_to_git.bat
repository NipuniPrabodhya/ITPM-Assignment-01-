@echo off
echo Finalizing GitHub Update...
git add .
git commit -m "update: Final artifacts, screenshots, and 60 test cases"
git push origin main
echo Done! Your assignment is now on GitHub.
pause
