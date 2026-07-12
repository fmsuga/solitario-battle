@echo off
REM build_exe.bat
REM ---------------
REM Genera el .exe con un solo doble-click. Corré esto parado en
REM Windows, adentro de la carpeta solitario_50.

echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install pillow pyinstaller

echo.
echo Limpiando compilaciones anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del SolitarioDeLasCincuentaCartas.spec 2>nul

echo.
echo Generando el ejecutable...
pyinstaller --onefile --windowed --name SolitarioDeLasCincuentaCartas --paths src --add-data "assets/cartas_img;assets/cartas_img" main_grafico.py

echo.
echo Listo. El ejecutable esta en dist\SolitarioDeLasCincuentaCartas.exe
pause
