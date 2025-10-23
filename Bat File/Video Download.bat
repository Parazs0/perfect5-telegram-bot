@echo off
setlocal enabledelayedexpansion

:: Define paths dynamically
set "YTDLP_EXE=%USERPROFILE%\Downloads\yt-dlp.exe"
set "FFMPEG_PATH=%USERPROFILE%\Downloads\ffmpeg-master-latest-win64-gpl-shared\bin"

:: Check if required tools exist
if not exist "%YTDLP_EXE%" (
    echo [ERROR] yt-dlp.exe not found at:
    echo "%YTDLP_EXE%"
    echo Please ensure the path is correct.
    pause
    exit /b
)

if not exist "%FFMPEG_PATH%\ffmpeg.exe" (
    echo [ERROR] ffmpeg.exe not found in:
    echo "%FFMPEG_PATH%"
    echo Please ensure the path is correct.
    pause
    exit /b
)

title Universal Video/Audio Downloader
echo ==========================================
echo       Universal Video/Audio Downloader
echo ==========================================
echo.
echo 1. Download MP4 (Video)
echo 2. Download MP3 (Audio)
echo.
set /p choice=Enter your choice (1 or 2): 

if "!choice!"=="1" (
    set format=bestvideo+bestaudio/best
    set extra=
) else if "!choice!"=="2" (
    set format=bestaudio
    set extra=--extract-audio --audio-format mp3 --audio-quality 0
) else (
    echo [ERROR] Invalid choice! Exiting...
    pause
    exit /b
)

echo.
set /p url=Paste video or audio link: 

echo.
echo [STATUS] Starting download...
echo.

"%YTDLP_EXE%" --ffmpeg-location "!FFMPEG_PATH!" -f !format! -o "%%(title)s.%%(ext)s" !extra! !url!

echo.
echo ==========================================
echo [SUCCESS] Download complete!
echo Check the current folder for your file.
echo ==========================================
pause
exit