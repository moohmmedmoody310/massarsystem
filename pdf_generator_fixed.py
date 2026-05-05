from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import HexColor, black, white, lightgrey
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
import os
import io
from datetime import datetime, timedelta
import arabic_reshaper
from bidi.algorithm import get_display

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ألوان مركز مسار الاحترافية
COLOR_PRIMARY = HexColor('#1a2615')
COLOR_SECONDARY = HexColor('#c5a059')
COLOR_ACCENT = HexColor('#2d3924')
COLOR_LIGHT = HexColor('#fbf9f4')
COLOR_DARK = HexColor('#161c12')
COLOR_SUCCESS = HexColor('#27ae60')
COLOR_WARNING = HexColor('#f39c12')
COLOR_DANGER = HexColor('#e74c3c')
COLOR_INFO = HexColor('#3498db')
COLOR_GRADIENT_START = HexColor('#1a2615')
COLOR_GRADIENT_END = HexColor('#2d3924')

def get_arabic_style(size=12, bold=False, color=None, align=TA_RIGHT, leading=None):
    """الحصول على ستايل عربي احترافي"""
    style = ParagraphStyle(
        'arabic',
        fontName='Helvetica-Bold' if bold else 'Helvetica',
        fontSize=size,
        textColor=color or COLOR_DARK,
        alignment=align,
        spaceAfter=4,
        leading=leading or size * 1.2,
        rightIndent=0,
        leftIndent=0,
        firstLineIndent=0,
        allowWidows=1,
        allowOrphans=1,
        wordWrap='LTR'
    )
    return style

def get_header_style():
    """ستايل احترافي للعناوين"""
    return ParagraphStyle(
        'header',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=20,
        leading=30,
        borderWidth=0,
        borderColor=COLOR_PRIMARY,
        borderPadding=5
    )

def get_subheader_style():
    """ستايل احترافي للعناوين الفرعية"""
    return ParagraphStyle(
        'subheader',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=COLOR_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=8,
        spaceBefore=12,
        leading=20
    )

def create_gradient_header(doc, title, subtitle=""):
    """إنشاء رأس احترافي مع تدرج لوني"""
    elements = []
    
    # إضافة مسافة في الأعلى
    elements.append(Spacer(1, 1*cm))
    
    # العنوان الرئيسي
    elements.append(Paragraph(title, get_header_style()))
    
    # العنوان الفرعي
    if subtitle:
        elements.append(Paragraph(subtitle, get_subheader_style()))
    
    # خط فاصل احترافي
    elements.append(HRFlowable(width="80%", thickness=2, color=COLOR_SECONDARY, spaceBefore=10, spaceAfter=20))
    
    return elements

def create_info_table(data, title="معلومات"):
    """إنشاء جدول معلومات احترافي"""
    elements = []
    
    # عنوان الجدول
    elements.append(Paragraph(title, get_arabic_style(14, bold=True, color=COLOR_PRIMARY)))
    
    # بيانات الجدول
    table_data = []
    for key, value in data.items():
        table_data.append([
            Paragraph(f'<b>{key}:</b>', get_arabic_style(11, bold=True, color=COLOR_DARK)),
            Paragraph(str(value), get_arabic_style(11, color=COLOR_DARK))
        ])
    
    # إنشاء الجدول
    table = Table(table_data, colWidths=[4*cm, 8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDINGS', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [COLOR_LIGHT, white]),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_DARK),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))
    
    return elements

def create_student_progress_chart(attendance_data, grades_data):
    """إنشاء رسم بياني لتقدم الطالب"""
    drawing = Drawing(8*cm, 4*cm)
    
    # رسم بياني للحضور
    if attendance_data:
        chart = VerticalBarChart()
        chart.width = 7*cm
        chart.height = 3.5*cm
        chart.x = 0.5*cm
        chart.y = 0.5*cm
        
        # بيانات الحضور
        data = [[len([a for a in attendance_data if a['status'] == 'present'])],
                [len([a for a in attendance_data if a['status'] == 'absent'])],
                [len([a for a in attendance_data if a['status'] == 'late'])]]
        
        chart.data = data
        chart.categoryAxis.visible = False
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(max(row) for row in data) + 1
        
        # ألوان الأعمدة
        chart.bars[0].fillColor = COLOR_SUCCESS
        chart.bars[1].fillColor = COLOR_DANGER
        chart.bars[2].fillColor = COLOR_WARNING
        
        drawing.add(chart)
    
    return drawing

def generate_advanced_student_receipt(student, payment, center_name="مركز مسار التعليمي"):
    """توليد إيصال دفع احترافي ومتقدم"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # رأس احترافي
    elements.extend(create_gradient_header(doc, center_name, "إيصال سداد رسوم دراسية"))
    
    # معلومات الإيصال
    receipt_info = {
        "رقم الإيصال": f"#{payment['id']:06d}",
        "التاريخ": datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "اسم الطالب": student['name'],
        "رقم الهاتف": student['phone'],
        "ولي الأمر": student.get('parent_name', '-'),
        "المبلغ": f"{payment['amount']:,.0f} جنيه",
        "طريقة الدفع": payment.get('payment_method', 'نقدي'),
        "الشهر": payment.get('month', '-'),
        "السنة": payment.get('year', datetime.now().year),
        "المستلم": payment.get('received_by', 'المدير')
    }
    
    elements.extend(create_info_table(receipt_info))
    
    # معلومات إضافية
    if payment.get('notes'):
        elements.append(Paragraph("ملاحظات", get_arabic_style(12, bold=True, color=COLOR_PRIMARY)))
        elements.append(Paragraph(payment['notes'], get_arabic_style(10, color=COLOR_DARK)))
        elements.append(Spacer(1, 0.5*cm))
    
    # تذييل احترافي
    elements.append(HRFlowable(width="80%", thickness=1, color=COLOR_SECONDARY, spaceBefore=20))
    
    footer_data = [
        [Paragraph("شكراً لثقتكم بـ", get_arabic_style(10, color=COLOR_ACCENT, align=TA_CENTER))],
        [Paragraph(center_name, get_arabic_style(12, bold=True, color=COLOR_PRIMARY, align=TA_CENTER))],
        [Paragraph("📞 | 📧 | 📍", get_arabic_style(8, color=COLOR_SECONDARY, align=TA_CENTER))]
    ]
    
    footer_table = Table(footer_data, colWidths=[15*cm])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDINGS', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(footer_table)
    
    # بناء الـ PDF
    doc.build(elements)
    buffer.seek(0)
    
    # حفظ الملف
    filename = f"receipt_{payment['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath, filename

def generate_ai_student_report(student, attendance_data, grades_data, payments_data, center_name="مركز مسار التعليمي"):
    """توليد تقرير ذكاء اصطناعي احترافي للطالب"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # رأس احترافي
    elements.extend(create_gradient_header(doc, center_name, "تقرير أداء الطالب"))
    
    # معلومات الطالب الأساسية
    student_info = {
        "اسم الطالب": student['name'],
        "رقم الهاتف": student['phone'],
        "ولي الأمر": student.get('parent_name', '-'),
        "هاتف ولي الأمر": student.get('parent_phone', '-'),
        "المجموعة": student.get('group_name', '-'),
        "تاريخ الانضمام": student.get('join_date', '-')
    }
    
    elements.extend(create_info_table(student_info, "معلومات الطالب"))
    
    # تحليل الأداء بالذكاء الاصطناعي
    elements.append(Paragraph("📊 تحليل الأداء الذكي", get_arabic_style(14, bold=True, color=COLOR_PRIMARY)))
    
    # حساب الإحصائيات
    total_days = len(attendance_data) if attendance_data else 0
    present_days = len([a for a in attendance_data if a['status'] == 'present']) if attendance_data else 0
    absent_days = len([a for a in attendance_data if a['status'] == 'absent']) if attendance_data else 0
    late_days = len([a for a in attendance_data if a['status'] == 'late']) if attendance_data else 0
    
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
    
    # تحليل الدرجات
    avg_grade = 0
    if grades_data:
        grades = [g['score'] for g in grades_data if g.get('score')]
        avg_grade = sum(grades) / len(grades) if grades else 0
    
    # تحليل المدفوعات
    total_paid = sum(p['amount'] for p in payments_data) if payments_data else 0
    
    # إنشاء تقرير الذكاء الاصطناعي
    ai_analysis = f"""
    🎯 **نظرة عامة على الأداء:**
    
    • نسبة الحضور: {attendance_rate:.1f}% ({present_days} من {total_days} يوم)
    • أيام الغياب: {absent_days} يوم
    • أيام التأخير: {late_days} يوم
    • متوسط الدرجات: {avg_grade:.1f}%
    • إجمالي المدفوعات: {total_paid:,.0f} جنيه
    
    📈 **تحليل النمو:**
    
    """
    
    # إضافة تحليل متقدم
    if attendance_rate >= 90:
        ai_analysis += "• ✅ أداء حضور ممتاز - الطالب منتظم جداً\n"
    elif attendance_rate >= 75:
        ai_analysis += "• ⚠️ أداء حضور جيد - يحتاج لتحسين الانتظام\n"
    else:
        ai_analysis += "• ❌ أداء حضور ضعيف - يحتاج لمتابعة فورية\n"
    
    if avg_grade >= 85:
        ai_analysis += "• 🌟 مستوى أكاديمي ممتاز\n"
    elif avg_grade >= 70:
        ai_analysis += "• 📚 مستوى أكاديمي جيد\n"
    else:
        ai_analysis += "• 📖 يحتاج لدعم أكاديمي إضافي\n"
    
    elements.append(Paragraph(ai_analysis, get_arabic_style(11, color=COLOR_DARK)))
    elements.append(Spacer(1, 0.5*cm))
    
    # جدول الحضور التفصيلي
    if attendance_data:
        elements.append(Paragraph("📅 سجل الحضور", get_arabic_style(12, bold=True, color=COLOR_PRIMARY)))
        
        attendance_table_data = [["التاريخ", "الحالة", "ملاحظات"]]
        for record in attendance_data[:10]:  # آخر 10 أيام
            status_text = "حاضر" if record['status'] == 'present' else "غائب" if record['status'] == 'absent' else "متأخر"
            status_color = COLOR_SUCCESS if record['status'] == 'present' else COLOR_DANGER if record['status'] == 'absent' else COLOR_WARNING
            
            attendance_table_data.append([
                record.get('date', '-'),
                Paragraph(status_text, get_arabic_style(10, color=status_color)),
                record.get('notes', '-')
            ])
        
        attendance_table = Table(attendance_table_data, colWidths=[3*cm, 3*cm, 6*cm])
        attendance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, COLOR_ACCENT),
            ('PADDINGS', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(attendance_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # تذييل احترافي
    elements.append(HRFlowable(width="80%", thickness=1, color=COLOR_SECONDARY, spaceBefore=20))
    
    footer_text = f"""
    تم إنشاء هذا التقرير باستخدام تقنيات الذكاء الاصطناعي
    {center_name} - {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
    """
    
    elements.append(Paragraph(footer_text, get_arabic_style(9, color=COLOR_ACCENT, align=TA_CENTER)))
    
    # بناء الـ PDF
    doc.build(elements)
    buffer.seek(0)
    
    # حفظ الملف
    filename = f"ai_report_{student['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath, filename

def generate_financial_report(financial_data, center_name="مركز مسار التعليمي"):
    """توليد تقرير مالي احترافي"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # رأس احترافي
    elements.extend(create_gradient_header(doc, center_name, "التقرير المالي"))
    
    # ملخص مالي
    total_income = financial_data.get('total_income', 0)
    total_expenses = financial_data.get('total_expenses', 0)
    net_profit = total_income - total_expenses
    teacher_salaries = financial_data.get('teacher_salaries', 0)
    
    financial_summary = {
        "إجمالي الإيرادات": f"{total_income:,.0f} جنيه",
        "إجمالي المصروفات": f"{total_expenses:,.0f} جنيه",
        "رواتب المعلمين": f"{teacher_salaries:,.0f} جنيه",
        "صافي الربح": f"{net_profit:,.0f} جنيه",
        "فترة التقرير": financial_data.get('period', 'شهر الحالي')
    }
    
    elements.extend(create_info_table(financial_summary, "الملخص المالي"))
    
    # تحليل الأداء المالي
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
    salary_ratio = (teacher_salaries / total_income * 100) if total_income > 0 else 0
    
    elements.append(Paragraph("📊 تحليل الأداء المالي", get_arabic_style(14, bold=True, color=COLOR_PRIMARY)))
    
    analysis_text = f"""
    • هامش الربح: {profit_margin:.1f}%
    • نسبة الرواتب للإيرادات: {salary_ratio:.1f}%
    • متوسط الدخل الشهري: {total_income:,.0f} جنيه
    """
    
    if profit_margin >= 30:
        analysis_text += "• ✅ أداء مالي ممتاز\n"
    elif profit_margin >= 15:
        analysis_text += "• ⚠️ أداء مالي جيد\n"
    else:
        analysis_text += "• ❌ يحتاج لتحسين الأداء المالي\n"
    
    elements.append(Paragraph(analysis_text, get_arabic_style(11, color=COLOR_DARK)))
    
    # بناء الـ PDF
    doc.build(elements)
    buffer.seek(0)
    
    # حفظ الملف
    filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath, filename
