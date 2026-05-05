@echo off
chcp 65001 >nul
title مركز جمال ناصر التعليمي - تثبيت النظام
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║       مركز جمال ناصر التعليمي - نظام الإدارة       ║
echo  ║              جاري تثبيت النظام...                   ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: التحقق من Python
echo [1/6] التحقق من Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطأ] Python غير مثبت!
    echo يرجى تحميل Python من: https://www.python.org/downloads/
    echo تأكد من تفعيل "Add Python to PATH" أثناء التثبيت
    pause
    exit /b 1
)
echo       ✓ Python موجود

:: تثبيت المكتبات
echo.
echo [2/6] تثبيت المكتبات المطلوبة...
pip install flask openpyxl reportlab --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [خطأ] فشل تثبيت المكتبات
    pause
    exit /b 1
)
echo       ✓ تم تثبيت المكتبات

:: إنشاء المجلدات
echo.
echo [3/6] إنشاء مجلدات النظام...
if not exist "database" mkdir database
if not exist "reports" mkdir reports
if not exist "exports" mkdir exports
if not exist "templates" mkdir templates
echo       ✓ تم إنشاء المجلدات

:: تهيئة قاعدة البيانات
echo.
echo [4/6] تهيئة قاعدة البيانات...
python -c "from database import init_db; init_db()"
if errorlevel 1 (
    echo [خطأ] فشل تهيئة قاعدة البيانات
    pause
    exit /b 1
)
echo       ✓ تم إنشاء قاعدة البيانات

:: إنشاء ملف التشغيل
echo.
echo [5/6] إنشاء اختصار التشغيل...
echo @echo off > run_center.bat
echo chcp 65001 ^>nul >> run_center.bat
echo title مركز جمال ناصر التعليمي >> run_center.bat
echo color 0A >> run_center.bat
echo echo. >> run_center.bat
echo echo  ╔══════════════════════════════════════════╗ >> run_center.bat
echo echo  ║    مركز جمال ناصر التعليمي يعمل الآن   ║ >> run_center.bat
echo echo  ║    افتح المتصفح على: localhost:5000     ║ >> run_center.bat
echo echo  ║    المستخدم: admin                      ║ >> run_center.bat
echo echo  ║    كلمة المرور: admin123                ║ >> run_center.bat
echo echo  ╚══════════════════════════════════════════╝ >> run_center.bat
echo echo. >> run_center.bat
echo start "" http://localhost:5000 >> run_center.bat
echo python app.py >> run_center.bat
echo pause >> run_center.bat

:: إنشاء اختصار على سطح المكتب
echo.
echo [6/6] إنشاء اختصار على سطح المكتب...
set SCRIPT_DIR=%~dp0
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\مركز جمال ناصر.lnk'); $s.TargetPath = '%SCRIPT_DIR%run_center.bat'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = 'shell32.dll,23'; $s.Description = 'نظام مركز جمال ناصر التعليمي'; $s.Save()" >nul 2>&1
echo       ✓ تم إنشاء الاختصار

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║              ✓ تم التثبيت بنجاح!                   ║
echo  ║                                                      ║
echo  ║   لتشغيل النظام: اضغط على أيقونة سطح المكتب       ║
echo  ║   أو افتح run_center.bat                           ║
echo  ║                                                      ║
echo  ║   المستخدم: admin    كلمة المرور: admin123          ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
set /p START_NOW=هل تريد تشغيل النظام الآن؟ (y/n): 
if /i "%START_NOW%"=="y" (
    start run_center.bat
)
pause
