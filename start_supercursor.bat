@echo off
title SuperCursor - Personal AI Screen & Cursor Companion
echo ========================================================
echo   SuperCursor: Starting Personal AI Desktop Companion...
echo ========================================================
python main.py
if errorlevel 1 (
    echo.
    echo Something went wrong while running SuperCursor.
    pause
)
