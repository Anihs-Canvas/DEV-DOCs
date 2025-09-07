@echo off
echo Opening Kubernetes documentation...
echo.
echo Trying different methods:
echo.

echo 1. Trying default browser...
start "" "C:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\Kubernetes.html"
timeout /t 2 /nobreak > nul

echo 2. Trying Internet Explorer...
start "" "C:\Program Files\Internet Explorer\iexplore.exe" "C:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\Kubernetes.html"
timeout /t 2 /nobreak > nul

echo 3. Trying Edge...
start msedge "file:///C:/Users/owner/Desktop/DEV-DOCs/KUBERNETES/Kubernetes.html"
timeout /t 2 /nobreak > nul

echo 4. Trying Chrome...
start chrome "file:///C:/Users/owner/Desktop/DEV-DOCs/KUBERNETES/Kubernetes.html"
timeout /t 2 /nobreak > nul

echo 5. Via HTTP server (localhost:8080/Kubernetes.html)
start "" "http://localhost:8080/Kubernetes.html"

echo.
echo If none of these work, try:
echo 1. Right-click Kubernetes.html and select "Open with" -> Browser
echo 2. Open your browser and drag the file into it
echo 3. Or go to http://localhost:8080/Kubernetes.html
pause