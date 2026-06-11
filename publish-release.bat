@echo off
set VERSION=%1
set ZIP=windepot.zip

echo Creating git tag %VERSION%...

git add %ZIP%
git commit -m "Release %VERSION%"
git tag %VERSION%
git push origin main
git push origin %VERSION%

echo Done.
pause