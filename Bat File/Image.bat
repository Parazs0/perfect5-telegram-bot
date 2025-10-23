@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Frame Extractor v3.3 - Creates 'Images' subfolder
title Video Frame Extractor - Images Subfolder

:: Check for FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg not found. Please add FFmpeg to your system PATH.
    pause
    exit
)

:: User Input with Default Path
echo.
echo ==========================================
echo    Video Frame Extractor Script
echo ==========================================
echo.
set "default_path=C:\Users\Gandhi\Documents\Bat File\"
echo [INPUT] Drag and drop your video file into this window
echo         or enter the full path manually.
echo.
set /p "video_path=Video Path (e.g., C:\Users\User\video.mp4): "
echo.

:: Trim quotes and spaces from input
set "video_path=!video_path:"=!"
set "video_path=!video_path: =!"

:: Validation loop
:validate
if not exist "!video_path!" (
    echo [ERROR] The specified video file was not found.
    set /p "video_path=Please enter the correct path again: "
    set "video_path=!video_path:"=!"
    set "video_path=!video_path: =!"
    goto validate
)

:: Create 'Images' subfolder in the video's directory
for %%a in ("!video_path!") do set "output_dir=%%~dpaImages\"
mkdir "!output_dir!" 2>nul

:: FFmpeg Processing with Progress
echo [STATUS] Extracting frames from: !video_path!
echo          Frames will be saved in: !output_dir!
echo.

:: Smart FFmpeg Command
ffmpeg -hide_banner -y -i "!video_path!" ^
       -vsync 0 -threads 4 -stats ^
       -qscale:v 2 "!output_dir!frame_%%04d.jpg"

:: Completion with File Count
set count=0
for /f %%a in ('dir /a-d /b "!output_dir!frame_*.jpg" 2^>nul ^| find /c /v ""') do set count=%%a
echo.
echo ==========================================
echo [SUCCESS] !count! frames extracted to:
echo !output_dir!
echo ==========================================
echo.

:: Open output folder automatically
explorer "!output_dir!"
pause
exit