@echo off
title ⚡ Windows Junk Cleaner - Optimized
color 0A

:: Admin check
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Please run this script as Administrator.
    pause
    exit
)

echo ====================================================
echo        WINDOWS JUNK CLEANER - Optimized Version
echo ====================================================
echo.

set LOG=%TEMP%\cleanup_log.txt
echo Cleanup started at %date% %time% > "%LOG%"

:: Clean User Temp
echo [+] Cleaning User Temp Files...
if exist "%USERPROFILE%\AppData\Local\Temp\" (
    del /s /f /q "%USERPROFILE%\AppData\Local\Temp\*.*" >> "%LOG%" 2>&1
    for /d %%d in ("%USERPROFILE%\AppData\Local\Temp\*") do rd /s /q "%%d" >> "%LOG%" 2>&1
    echo     Done.
) else (
    echo     Skipped.
)

:: Clean System Temp
echo [+] Cleaning System Temp...
if exist "C:\Windows\Temp\" (
    del /s /f /q "C:\Windows\Temp\*.*" >> "%LOG%" 2>&1
    for /d %%d in ("C:\Windows\Temp\*") do rd /s /q "%%d" >> "%LOG%" 2>&1
    echo     Done.
) else (
    echo     Skipped.
)

:: Optional: Clean Prefetch
set /p PREFETCH=Do you want to clear Prefetch files? (Y/N): 
if /I "%PREFETCH%"=="Y" (
    echo [+] Cleaning Prefetch...
    if exist "C:\Windows\Prefetch\" (
        del /s /f /q "C:\Windows\Prefetch\*.*" >> "%LOG%" 2>&1
        echo     Done.
    )
)

:: Clean Recent
echo [+] Cleaning Recent Files...
if exist "%USERPROFILE%\Recent\" (
    del /s /f /q "%USERPROFILE%\Recent\*.*" >> "%LOG%" 2>&1
    echo     Done.
)

:: Empty Recycle Bin
echo [+] Emptying Recycle Bin...
if exist "C:\$Recycle.Bin" (
    rd /s /q "C:\$Recycle.Bin" >> "%LOG%" 2>&1
    echo     Done.
)

:: Windows Update Cache
echo [+] Cleaning Windows Update Cache...
net stop wuauserv >nul 2>&1
if exist "C:\Windows\SoftwareDistribution\Download\" (
    del /s /f /q "C:\Windows\SoftwareDistribution\Download\*.*" >> "%LOG%" 2>&1
    for /d %%d in ("C:\Windows\SoftwareDistribution\Download\*") do rd /s /q "%%d" >> "%LOG%" 2>&1
    echo     Done.
)
net start wuauserv >nul 2>&1

echo.
echo ====================================================
echo Cleanup Complete! Log saved to: %LOG%
echo ====================================================
pause
exit
