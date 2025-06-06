@echo off
title Rebuilding Snake Battle Arena Distribution
echo ========================================
echo    REBUILDING DISTRIBUTION PACKAGE
echo ========================================
echo.

REM Clean up old builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "SnakeBattleArena_Distribution" rmdir /s /q "SnakeBattleArena_Distribution"

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Building new executable...
pyinstaller SnakeBattleArena.spec --clean --noconfirm

if not exist "dist\SnakeBattleArena.exe" (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Creating distribution package...
mkdir "SnakeBattleArena_Distribution"
copy "dist\SnakeBattleArena.exe" "SnakeBattleArena_Distribution\"

echo.
echo Creating START_GAME.bat...
(
echo @echo off
echo title Snake Battle Arena
echo cls
echo echo ========================================
echo echo       SNAKE BATTLE ARENA
echo echo ========================================
echo echo.
echo echo Starting multiplayer snake game...
echo echo Your browser will open automatically
echo echo Share your network IP with friends!
echo echo.
echo echo ========================================
echo echo IMPORTANT INSTRUCTIONS:
echo echo 1. This will start the game server on your computer
echo echo 2. Your browser will open automatically
echo echo 3. To play with friends, share your network IP address
echo echo 4. Friends can connect using: http://YOUR_IP:5000
echo echo 5. Press Ctrl+C in this window to stop the server
echo echo ========================================
echo echo.
echo echo Starting Snake Battle Arena...
echo echo.
echo echo The game will open in your default browser
echo echo Check the console window for your network IP address
echo echo Share that IP with friends to play multiplayer!
echo echo.
echo.
echo "SnakeBattleArena.exe"
echo.
echo echo.
echo echo Game server stopped.
echo pause
) > "SnakeBattleArena_Distribution\START_GAME.bat"

echo.
echo Creating README...
copy "README.md" "SnakeBattleArena_Distribution\"

echo.
echo ========================================
echo ✅ DISTRIBUTION PACKAGE READY!
echo ========================================
echo.
echo Location: SnakeBattleArena_Distribution\
echo.
echo To test: cd SnakeBattleArena_Distribution && START_GAME.bat
echo.
echo ========================================
pause