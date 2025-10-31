@echo off
echo ====================================
echo Processador em Lote de Audio ECO5000
echo ====================================
echo.
echo Processando arquivos...
echo Filtros: Highpass 400 Hz, Lowpass 1000 Hz
echo.
python batch_process_audio.py
echo.
pause

