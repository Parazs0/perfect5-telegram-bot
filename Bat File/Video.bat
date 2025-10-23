@echo off
cd /d "C:\Users\Gandhi\Documents\Bat File"

:: Step 1: Create interpolated 60 FPS video from 30 FPS images
ffmpeg -framerate 30 -i "Images\frame_%%04d.jpg" -vf "minterpolate=fps=60" -c:v libx264 -pix_fmt yuv420p temp_video.mp4

:: Step 2: Add audio
ffmpeg -i temp_video.mp4 -i "Audio.mp3" -c:v copy -c:a aac -shortest Final_Video.mp4

:: Step 3: Optional - stabilize the final video
ffmpeg -i Final_Video.mp4 -vf deshake -c:a copy Final_Stable.mp4

:: Step 4: Clean up
del temp_video.mp4
del Final_Video.mp4

echo ✅ 60 FPS Stable Video created: Final_Stable.mp4
pause
