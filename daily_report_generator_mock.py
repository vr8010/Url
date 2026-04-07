#!/usr/bin/env python3
"""
Daily Report Generator for URL Shortener Analytics (Mock Version)
Generates a PDF report of top 10 clicked short URLs and sends via email
This version uses mock data for demonstration without requiring a database
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
import os
import random


class DailyReportGenerator:
    """Generate and email daily analytics report for URL shortener"""
    
    def __init__(self, email_config=None):
        """
        Initialize report generator
        
        Args:
            email_config: Dict with email configuration (optional for demo)
        """
        self.email_config = email_config
        self.report_filename = f"url_analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    def fetch_top_urls_mock(self, limit=10):
        """
        Generate mock data for demonstration
        
        Args:
            limit: Number of top URLs to generate
            
        Returns:
            List of dictionaries with URL data
        """
        mock_domains = [
            'github.com/user/repo',
            'stackoverflow.com/questions/12345',
            'medium.com/article-title',
            'youtube.com/watch?v=abc123',
            'docs.python.org/3/library',
            'reddit.com/r/programming',
            'dev.to/article-name',
            'twitter.com/user/status',
            'linkedin.com/in/profile',
            'amazon.com/product/dp'
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
        
        # Sort by click count
        data.sort(key=lambda x: x['click_count'], reverse=True)
        return data
    
    def generate_pdf(self, data):
        """
        Generate PDF report using reportlab
        
        Args:
            data: List of URL analytics data
        """
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
            alignment=1  # Center
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
        
        # Table data
        table_data = [['Rank', 'Short Code', 'Original URL', 'Clicks', 'Last Clicked']]
        
        for idx, row in enumerate(data, 1):
            original_url = row['original']
            if len(original_url) > 40:
                original_url = original_url[:37] + '...'
            
            last_clicked = row['last_clicked'].strftime('%Y-%m-%d %H:%M') if row['last_clicked'] else 'N/A'
            
            table_data.append([
                str(idx),
                row['short_code'],
                original_url,
                str(row['click_count']),
                last_clicked
            ])
        
        # Create table
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
        
        # Build PDF
        doc.build(elements)
        print(f"✓ PDF generated successfully: {self.report_filename}")
    
    def send_email(self):
        """Send the generated PDF report via email"""
        if not self.email_config:
            print("⚠ Email configuration not provided. Skipping email send.")
            print(f"  PDF saved as: {self.report_filename}")
            return True
        
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from_email']
        msg['To'] = self.email_config['to_email']
        msg['Subject'] = f"Daily URL Analytics Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Email body
        body = f"""
        Hello,
        
        Please find attached the daily URL analytics report for {datetime.now().strftime('%B %d, %Y')}.
        
        This report contains the top 10 most clicked short URLs from the last 24 hours.
        
        Best regards,
        URL Shortener Analytics System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        try:
            with open(self.report_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {self.report_filename}'
                )
                msg.attach(part)
        except Exception as e:
            print(f"✗ Error attaching PDF: {e}")
            return False
        
        # Send email
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"✓ Email sent successfully to {self.email_config['to_email']}")
            return True
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def generate_and_send_report(self, use_mock=True):
        """Main method to generate report and send via email"""
        print("=" * 60)
        print("URL Shortener - Daily Analytics Report Generator")
        print("=" * 60)
        
        if use_mock:
            print("\n📊 Generating mock data for demonstration...")
            data = self.fetch_top_urls_mock(limit=10)
        else:
            print("\n📊 Fetching top URLs data from database...")
            # This would call the real database method
            data = []
        
        if not data:
            print("✗ No data available for report generation")
            return False
        
        print(f"✓ Retrieved {len(data)} URL entries")
        
        print("\n📄 Generating PDF report...")
        self.generate_pdf(data)
        
        print("\n📧 Processing email...")
        success = self.send_email()
        
        print("\n" + "=" * 60)
        if success:
            print("✓ Report generation completed successfully!")
        else:
            print("⚠ Report generated but email sending failed")
        print("=" * 60)
        
        return success


def main():
    """Main execution function"""
    
    # Email configuration (optional - leave None for demo mode)
    email_config = None
    
    # Uncomment and configure to enable email sending:
    # email_config = {
    #     'smtp_server': 'smtp.gmail.com',
    #     'smtp_port': 587,
    #     'from_email': '[email protected]',
    #     'to_email': '[email protected]',
    #     'username': '[email protected]',
    #     'password': 'your_app_password'
    # }
    
    # Generate and send report
    generator = DailyReportGenerator(email_config)
    generator.generate_and_send_report(use_mock=True)


if __name__ == "__main__":
    main()
