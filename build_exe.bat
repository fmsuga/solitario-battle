@echo off
setlocal

REM ==========================================
REM Build del ejecutable - Solitario de las 50
REM ==========================================

echo.
echo [1/3] Actualizando e instalando dependencias...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

REM pygame-ce conserva el modulo `pygame` y ofrece wheel para Python 3.14.
python -m pip install --upgrade pillow pygame-ce pyinstaller
if errorlevel 1 goto :error

echo.
echo [2/3] Limpiando compilaciones anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q SolitarioBattle.spec 2>nul

echo.
echo [3/3] Generando ejecutable...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --clean ^
    --noupx ^
    --name SolitarioBattle ^
    --paths src ^
    --add-data "assets/cartas_img;assets/cartas_img" ^
    --add-data "assets/sonidos;assets/sonidos" ^
    main.py

if errorlevel 1 goto :error

echo.
echo ==========================================
echo Compilacion finalizada correctamente.
echo.
echo El ejecutable se encuentra en:
echo     dist\SolitarioBattle.exe
echo ==========================================
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo ERROR: La compilacion fallo.
echo Revisa los mensajes mostrados arriba.
echo ==========================================
echo.
pause
exit /b 1
