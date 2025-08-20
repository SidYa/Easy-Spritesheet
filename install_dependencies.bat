@echo off
echo Встановлення необхідних модулів для Easy Spritesheet...

:: Перевірка наявності Python
py --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python не знайдено. Перевірте, чи встановлено Python та чи додано його до PATH.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

:: Встановлення необхідних модулів
echo Встановлення Pillow (PIL)...
%PYTHON_CMD% -m pip install pillow

echo Встановлення tkinterdnd2...
%PYTHON_CMD% -m pip install tkinterdnd2

echo Всі необхідні модулі встановлено!
echo Тепер ви можете запустити програму за допомогою run.vbs

pause