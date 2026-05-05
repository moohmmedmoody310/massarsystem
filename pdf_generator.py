from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os
import io
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ألوان السنتر
COLOR_PRIMARY = colors.HexColor('#1a2615')
COLOR_SECONDARY = colors.HexColor('#c5a059')
COLOR_ACCENT = colors.HexColor('#2d3924')
COLOR_LIGHT = colors.HexColor('#fbf9f4')
COLOR_DARK = colors.HexColor('#161c12')
COLOR_RED = colors.HexColor('#e74c3c')
COLOR_GOLD = colors.HexColor('#c5a059')

def get_arabic_style(size=12, bold=False, color=None, align=TA_RIGHT):
    style = ParagraphStyle(
        'arabic',
        fontName='Helvetica-Bold' if bold else 'Helvetica',
        fontSize=size,
        textColor=color or COLOR_DARK,
        alignment=align,
        spaceAfter=4,
    )
    return style

def generate_student_receipt(student, payment, center_name="مركز مسار التعليمي"):
    """توليد إيصال دفع للطالب"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    
    # رأس الإيصال
    header_data = [
        [Paragraph(f'<b>{center_name}</b>', get_arabic_style(18, bold=True, color=COLOR_PRIMARY, align=TA_CENTER))],
        [Paragraph('إيصال سداد رسوم دراسية', get_arabic_style(14, color=COLOR_SECONDARY, align=TA_CENTER))],
        [Paragraph(f'رقم الإيصال: #{payment["id"]:04d}', get_arabic_style(11, color=colors.grey, align=TA_CENTER))],
    ]
    
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,1), (-1,1), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), COLOR_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [5,5,0,0]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))
    
    # معلومات الطالب
    student_data = [
        ['البيانات', 'المعلومات'],
        ['اسم الطالب:', student.get('name', '')],
        ['ولي الأمر:', student.get('parent_name', '')],
        ['المرحلة الدراسية:', student.get('grade_name', '')],
        ['رقم الهاتف:', student.get('parent_phone', '')],
    ]
    
    student_table = Table(student_data, colWidths=[8.5*cm, 8.5*cm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.5*cm))
    
    # تفاصيل الدفع
    months_ar = {
        '1': 'يناير', '2': 'فبراير', '3': 'مارس', '4': 'أبريل',
        '5': 'مايو', '6': 'يونيو', '7': 'يوليو', '8': 'أغسطس',
        '9': 'سبتمبر', '10': 'أكتوبر', '11': 'نوفمبر', '12': 'ديسمبر'
    }
    month_name = months_ar.get(str(payment.get('month', '')), payment.get('month', ''))
    
    payment_data = [
        ['تفاصيل الدفع', ''],
        ['الشهر:', f'{month_name} {payment.get("year", "")}'],
        ['طريقة الدفع:', 'كاش' if payment.get('payment_method') == 'cash' else payment.get('payment_method', '')],
        ['تاريخ الدفع:', payment.get('payment_date', '')[:10] if payment.get('payment_date') else ''],
        ['استلم بواسطة:', payment.get('received_by', 'الإدارة')],
    ]
    
    payment_table = Table(payment_data, colWidths=[8.5*cm, 8.5*cm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('SPAN', (0,0), (-1,0)),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 0.5*cm))
    
    # المبلغ المدفوع (بارز)
    amount_data = [
        [Paragraph(f'المبلغ المدفوع: {payment.get("amount", 0):,.0f} جنيه', 
                   get_arabic_style(20, bold=True, color=colors.white, align=TA_CENTER))]
    ]
    amount_table = Table(amount_data, colWidths=[17*cm])
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_ACCENT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('ROUNDEDCORNERS', [8,8,8,8]),
    ]))
    story.append(amount_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ملاحظات
    if payment.get('notes'):
        story.append(Paragraph(f'ملاحظات: {payment["notes"]}', 
                               get_arabic_style(11, color=colors.grey)))
    
    # التذييل
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f'{center_name} | تم إصدار هذا الإيصال بتاريخ {datetime.now().strftime("%Y/%m/%d %H:%M")}',
        get_arabic_style(9, color=colors.grey, align=TA_CENTER)
    ))
    story.append(Paragraph(
        'هذا الإيصال دليل على سداد الرسوم - يرجى الاحتفاظ به',
        get_arabic_style(9, color=COLOR_SECONDARY, align=TA_CENTER)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_monthly_report(students_data, month, year, center_name="مركز مسار التعليمي"):
    """توليد تقرير شهري للمدفوعات"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    months_ar = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    
    story.append(Paragraph(center_name, get_arabic_style(18, bold=True, color=COLOR_PRIMARY, align=TA_CENTER)))
    story.append(Paragraph(f'التقرير الشهري - {months_ar.get(month, month)} {year}', 
                           get_arabic_style(14, color=COLOR_SECONDARY, align=TA_CENTER)))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARY))
    story.append(Spacer(1, 0.5*cm))
    
    # جدول البيانات
    headers = ['#', 'اسم الطالب', 'المرحلة', 'المبلغ المطلوب', 'المدفوع', 'الحالة']
    table_data = [headers]
    
    total_required = 0
    total_paid = 0
    
    for i, s in enumerate(students_data, 1):
        status = 'مدفوع' if s.get('paid') else 'غير مدفوع'
        table_data.append([
            str(i),
            s.get('name', ''),
            s.get('grade_name', ''),
            f'{s.get("required_amount", 0):,.0f}',
            f'{s.get("paid_amount", 0):,.0f}',
            status
        ])
        total_required += s.get('required_amount', 0)
        total_paid += s.get('paid_amount', 0)
    
    # صف الإجمالي
    table_data.append(['', 'الإجمالي', '', f'{total_required:,.0f}', f'{total_paid:,.0f}', ''])
    
    col_widths = [1*cm, 5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    data_table = Table(table_data, colWidths=col_widths)
    
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, COLOR_LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), COLOR_GOLD),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ])
    
    # تلوين الحالة
    for i, s in enumerate(students_data, 1):
        if s.get('paid'):
            style.add('TEXTCOLOR', (5,i), (5,i), COLOR_ACCENT)
        else:
            style.add('TEXTCOLOR', (5,i), (5,i), COLOR_RED)
    
    data_table.setStyle(style)
    story.append(data_table)
    story.append(Spacer(1, 1*cm))
    
    # ملخص
    summary_data = [
        ['إجمالي المطلوب:', f'{total_required:,.0f} جنيه'],
        ['إجمالي المحصّل:', f'{total_paid:,.0f} جنيه'],
        ['المتبقي:', f'{total_required - total_paid:,.0f} جنيه'],
        ['نسبة التحصيل:', f'{(total_paid/total_required*100) if total_required > 0 else 0:.1f}%'],
    ]
    
    summary_table = Table(summary_data, colWidths=[8.5*cm, 8.5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_LIGHT),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_SECONDARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(summary_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
