@echo off
setlocal enabledelayedexpansion

REM User se folder ka path puchhna
set /p folder="Enter the full path of the folder containing videos: "

REM Agar folder nahi diya to exit
if "%folder%"=="" (
    echo No folder entered. Exiting.
    pause
    exit /b
)

REM Folder exist karta hai ya nahi check karna
if not exist "%folder%" (
    echo Folder "%folder%" does not exist!
    pause
    exit /b
)

set count=1

REM Sabhi video files convert karna
for %%f in ("%folder%\*.mp4" "%folder%\*.mov" "%folder%\*.avi" "%folder%\*.mkv" "%folder%\*.webm") do (
    ffmpeg -i "%%f" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -r 30 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "%folder%\reel_!count!.mp4"
    set /a count=!count!+1
)

echo Sabhi videos reels format me convert ho gaye.
pause
