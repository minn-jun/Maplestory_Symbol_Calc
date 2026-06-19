@echo off
setlocal

cd /d "%~dp0.."
taskkill /IM MapleSymbolOptimizer.exe /F >nul 2>nul
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
