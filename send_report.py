#!/usr/bin/env python3
"""
Interactive Daily Report Generator with Email
Prompts user for email configuration and sends the report
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
import getpass


class ReportGenerator:
    """Generate and email daily analytics report"""
    
    def __init__(self):
        self.report_filename = f"url_analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    def generate_mock_data(self, limit=10):
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
    
    def generate_pdf(self, data):
        """Generate PDF report using reportlab"""
        doc = SimpleDocTemplate(self.report_filename, pagesize=letter)
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
        print(f"✓ PDF generated: {self.report_filename}")
    
    def send_email(self, email_config):
        """Send PDF report via email"""
        msg = MIMEMultipart()
        msg['From'] = email_config['from_email']
        msg['To'] = email_config['to_email']
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
        with open(self.report_filename, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={self.report_filename}')
            msg.attach(part)
        
        # Send email
        print(f"\n📧 Connecting to {email_config['smtp_server']}...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(email_config['username'], email_config['password'])
        
        print(f"📤 Sending email to {email_config['to_email']}...")
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent successfully!")


def get_email_config():
    """Prompt user for email configuration"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION")
    print("="*60)
    
    print("\nNote: For Gmail, you need to use an App Password")
    print("Generate one at: https://myaccount.google.com/apppasswords")
    
    config = {}
    
    # SMTP Server
    print("\n1. SMTP Server (press Enter for Gmail default):")
    smtp = input("   SMTP Server [smtp.gmail.com]: ").strip()
    config['smtp_server'] = smtp if smtp else 'smtp.gmail.com'
    
    # SMTP Port
    print("\n2. SMTP Port (press Enter for default):")
    port = input("   Port [587]: ").strip()
    config['smtp_port'] = int(port) if port else 587
    
    # From Email
    print("\n3. Your Email Address:")
    config['from_email'] = input("   From: ").strip()
    config['username'] = config['from_email']
    
    # Password
    print("\n4. Email Password (App Password for Gmail):")
    print("   Note: Remove all spaces from App Password")
    password = getpass.getpass("   Password: ")
    config['password'] = password.replace(" ", "").strip()
    
    # To Email
    print("\n5. Recipient Email Address:")
    config['to_email'] = input("   To: ").strip()
    
    return config


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("URL SHORTENER - DAILY ANALYTICS REPORT GENERATOR")
    print("="*60)
    
    # Get email configuration
    email_config = get_email_config()
    
    # Generate report
    print("\n" + "="*60)
    print("GENERATING REPORT")
    print("="*60)
    
    generator = ReportGenerator()
    
    print("\n📊 Generating mock analytics data...")
    data = generator.generate_mock_data(limit=10)
    print(f"✓ Generated {len(data)} URL entries")
    
    print("\n📄 Creating PDF report...")
    generator.generate_pdf(data)
    
    # Send email
    try:
        generator.send_email(email_config)
        print("\n" + "="*60)
        print("✓ SUCCESS! Report sent successfully!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error sending email: {e}")
        print(f"\nPDF saved locally as: {generator.report_filename}")
        print("\nCommon issues:")
        print("- Gmail: Use App Password, not regular password")
        print("- Enable 2-factor authentication first")
        print("- Check SMTP server and port settings")


if __name__ == "__main__":
    main()
