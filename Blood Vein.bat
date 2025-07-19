@echo off
REM Ativar ambiente virtual, se houver
REM call venv\Scripts\activate

echo Instalando requisitos...
pip install -r requirements.txt

echo Iniciando o programa...
python main.py

pause