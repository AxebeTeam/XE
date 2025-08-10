@echo off
echo ========================================
echo       Discord GIF Bot
echo ========================================
echo.

if not exist "config.json" (
    echo ❌ ملف config.json غير موجود!
    echo يرجى تشغيل setup.bat أولاً
    pause
    exit
)

echo 🤖 تشغيل البوت...
echo.
python discord_gif_bot.py

echo.
echo ========================================
echo       Bot Stopped
echo ========================================
pause
