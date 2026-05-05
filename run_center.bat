@echo off
chcp 65001 >nul
title مركز جمال ناصر التعليمي
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║    مركز جمال ناصر التعليمي يعمل الآن   ║
echo  ║    افتح المتصفح على: localhost:5000     ║
echo  ║    المستخدم: admin                      ║
echo  ║    كلمة المرور: admin123                ║
echo  ║    لإيقاف النظام: اضغط Ctrl+C          ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"
timeout /t 2 /nobreak >nul
start "" http://localhost:5000
python app.py
pause
