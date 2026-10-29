@echo off
rem Запуск игры Maze и веб-сервера на Windows без make (двойной клик или из cmd).
rem Веб-интерфейс откроется на http://localhost:9090 (PORT можно переопределить).
cd /d "%~dp0"
call gradlew.bat run
