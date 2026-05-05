import sqlite3
import os
import psycopg2
from datetime import datetime
import urllib.parse

# استخدام PostgreSQL على Railway.app أو SQLite محلياً
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL على Railway.app
    # تحويل DATABASE_URL إلى صيغة psycopg2
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    parsed = urllib.parse.urlparse(DATABASE_URL)

    def get_db():
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        return conn

    def close_db(conn):
        conn.close()
else:
    # SQLite محلياً
    DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'center.db')

    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def close_db(conn):
        conn.close()

def init_db():
    # إنشاء مجلد قاعدة البيانات فقط في حالة SQLite
    if not DATABASE_URL:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db()
    c = conn.cursor()

    # جدول المستخدمين والأدوار
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        full_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # جدول المراحل الدراسية
    c.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )''')

    # جدول المواد
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade_id INTEGER,
        FOREIGN KEY(grade_id) REFERENCES grades(id)
    )''')

    # جدول المعلمين
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        whatsapp TEXT,
        subject TEXT,
        salary REAL DEFAULT 0,
        notes TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # جدول المجموعات
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade_id INTEGER,
        teacher_id INTEGER,
        subject_id INTEGER,
        day_of_week TEXT,
        time_slot TEXT,
        monthly_fee REAL DEFAULT 0,
        max_students INTEGER DEFAULT 20,
        status TEXT DEFAULT 'active',
        FOREIGN KEY(grade_id) REFERENCES grades(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )''')

    # جدول الطلاب
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        parent_name TEXT,
        parent_phone TEXT,
        parent_whatsapp TEXT,
        grade_id INTEGER,
        group_id INTEGER,
        national_id TEXT,
        address TEXT,
        birth_date TEXT,
        join_date TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY(grade_id) REFERENCES grades(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )''')

    # جدول الدفعات
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        month TEXT NOT NULL,
        year INTEGER NOT NULL,
        payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
        payment_method TEXT DEFAULT 'cash',
        notes TEXT,
        received_by TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    # جدول الحضور والغياب
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        group_id INTEGER,
        date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'present',
        notes TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )''')

    # جدول الدرجات والنتائج
    c.execute('''CREATE TABLE IF NOT EXISTS grades_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER,
        exam_name TEXT,
        score REAL,
        max_score REAL DEFAULT 100,
        exam_date TEXT,
        notes TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    # جدول المصروفات
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        date TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    )''')

    # جدول رواتب المعلمين
    c.execute('''CREATE TABLE IF NOT EXISTS teacher_salaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        month TEXT NOT NULL,
        year INTEGER NOT NULL,
        paid_date TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id)
    )''')

    # إضافة بيانات أولية
    # المراحل الدراسية
    c.execute("SELECT COUNT(*) FROM grades")
    if c.fetchone()[0] == 0:
        grades_data = [
            ('الصف الأول الابتدائي', 'المرحلة الابتدائية'),
            ('الصف الثاني الابتدائي', 'المرحلة الابتدائية'),
            ('الصف الثالث الابتدائي', 'المرحلة الابتدائية'),
            ('الصف الرابع الابتدائي', 'المرحلة الابتدائية'),
            ('الصف الخامس الابتدائي', 'المرحلة الابتدائية'),
            ('الصف السادس الابتدائي', 'المرحلة الابتدائية'),
            ('الصف الأول الإعدادي', 'المرحلة الإعدادية'),
            ('الصف الثاني الإعدادي', 'المرحلة الإعدادية'),
            ('الصف الثالث الإعدادي', 'المرحلة الإعدادية'),
            ('الصف الأول الثانوي', 'المرحلة الثانوية'),
            ('الصف الثاني الثانوي', 'المرحلة الثانوية'),
            ('الصف الثالث الثانوي', 'المرحلة الثانوية'),
        ]
        c.executemany("INSERT INTO grades (name, description) VALUES (?, ?)", grades_data)

    # المواد الدراسية
    c.execute("SELECT COUNT(*) FROM subjects")
    if c.fetchone()[0] == 0:
        subjects = [
            ('رياضيات',), ('عربي',), ('إنجليزي',), ('علوم',),
            ('فيزياء',), ('كيمياء',), ('أحياء',), ('تاريخ',),
            ('جغرافيا',), ('تربية دينية',), ('لغة فرنسية',), ('حاسب آلي',)
        ]
        c.executemany("INSERT INTO subjects (name) VALUES (?)", subjects)

    # المستخدم الإداري الافتراضي
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        import hashlib
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
                  ('admin', password_hash, 'admin', 'مدير النظام'))

    conn.commit()
    conn.close()
    print("✓ تم تهيئة قاعدة البيانات بنجاح")

if __name__ == '__main__':
    init_db()
