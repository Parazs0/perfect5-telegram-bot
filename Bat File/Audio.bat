@echo off
set input="C:\Users\Gandhi\Documents\Bat File\Video.mp4"
set output="C:\Users\Gandhi\Documents\Bat File\Audio.mp3"

ffmpeg -i %input% -vn -acodec libmp3lame -q:a 2 %output%

echo Audio extract ho gaya: %output%
pause
