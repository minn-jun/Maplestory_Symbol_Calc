@echo off
setlocal

cd /d "%~dp0.."
powershell -NoProfile -Command "Get-Process MapleSymbolOptimizer -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
ping 127.0.0.1 -n 2 >nul
if exist dist\MapleSymbolOptimizer.exe del /F /Q dist\MapleSymbolOptimizer.exe
python -m PyInstaller --clean --noconfirm build_tools\MapleSymbolOptimizer-onefile.spec
if errorlevel 1 (
    echo.
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete.
echo Output: dist\MapleSymbolOptimizer.exe
echo If .env exists in the project root, it is bundled into the executable.
