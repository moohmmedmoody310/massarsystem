import sys
import os

# إضافة مجلد النظام إلى مسار Python
sys.path.insert(0, os.getcwd())

from app import app as application

# إعدادات Passenger
application = application
