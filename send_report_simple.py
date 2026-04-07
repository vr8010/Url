#!/usr/bin/env python3
"""
Simple Report Generator - Direct configuration
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import random


def generate_mock_data(limit=10):
    """Generate mock URL analytics data"""
    mock_domains = [
        'github.com/user/awesome-project',
        'stackoverflow.com/questions/python-tips',
        'medium.com/@author/best-practices',
        'youtube.com/watch?v=tutorial',
        'docs.python.org/3/library/datetime',
        'reddit.com/r/programming/hot',
        'dev.to/article/web-development',
        'twitter.com/techuser/status',
        'linkedin.com/in/developer-profile',
        'amazon.com/product/bestseller'
    ]
    
    data = []
    for i in range(limit):
        clicks = random.randint(50, 500)
        hours_ago = random.randint(1, 23)
        
        data.append({
            'short_code': f'abc{i+1:03d}',
            'original': f'https://{mock_domains[i]}',
            'click_count': clicks,
            'last_clicked': datetime.now() - timedelta(hours=hours_ago)
        })
    
    data.sort(key=lambda x: x['click_count'], reverse=True)
    return data


def generate_pdf(filename, data):
    """Generate PDF report"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph("Daily URL Analytics Report", title_style)
    elements.append(title)
    
    # Date
    date_text = f"Report Date: {datetime.now().strftime('%B %d, %Y')}"
    date_para = Paragraph(date_text, styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    summary_text = f"Top {len(data)} Most Clicked Short URLs (Last 24 Hours)"
    summary = Paragraph(summary_text, styles['Heading2'])
    elements.append(summary)
    elements.append(Spacer(1, 0.2*inch))
    
    # Table
    table_data = [['Rank', 'Short Code', 'Original URL', 'Clicks', 'Last Clicked']]
    
    for idx, row in enumerate(data, 1):
        original_url = row['original']
        if len(original_url) > 40:
            original_url = original_url[:37] + '...'
        
        last_clicked = row['last_clicked'].strftime('%Y-%m-%d %H:%M')
        
        table_data.append([
            str(idx),
            row['short_code'],
            original_url,
            str(row['click_count']),
            last_clicked
        ])
    
    table = Table(table_data, colWidths=[0.6*inch, 1.2*inch, 3*inch, 0.8*inch, 1.5*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = "Generated automatically by URL Shortener Analytics System"
    footer = Paragraph(footer_text, styles['Italic'])
    elements.append(footer)
    
    doc.build(elements)


def send_email(from_email, password, to_email, pdf_file):
    """Send email with PDF attachment"""
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"Daily URL Analytics Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    body = f"""
Hello,

Please find attached the daily URL analytics report for {datetime.now().strftime('%B %d, %Y')}.

This report contains the top 10 most clicked short URLs from the last 24 hours.

Best regards,
URL Shortener Analytics System
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    with open(pdf_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={pdf_file}')
        msg.attach(part)
    
    # Send
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()


def main():
    print("="*60)
    print("URL SHORTENER - DAILY REPORT GENERATOR")
    print("="*60)
    
    # CONFIGURE HERE - Your email credentials
    FROM_EMAIL = "vishalrathod80053@gmail.com"
    APP_PASSWORD = "zjebghibysswnsxq"  # App Password (spaces removed)
    
    # Ask user for recipient email
    print("\n📧 Enter recipient email address:")
    TO_EMAIL = input("   To: ").strip()
    
    if not TO_EMAIL:
        print("✗ Email address cannot be empty!")
        return
    
    filename = f"url_analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    try:
        print("\n📊 Generating mock data...")
        data = generate_mock_data(10)
        print(f"✓ Generated {len(data)} entries")
        
        print("\n📄 Creating PDF report...")
        generate_pdf(filename, data)
        print(f"✓ PDF created: {filename}")
        
        print("\n📧 Sending email...")
        send_email(FROM_EMAIL, APP_PASSWORD, TO_EMAIL, filename)
        print(f"✓ Email sent to {TO_EMAIL}")
        
        print("\n" + "="*60)
        print("✓ SUCCESS! Report sent successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"\nPDF saved as: {filename}")


if __name__ == "__main__":
    main()
