#!/usr/bin/env python3
"""
Daily Report Generator for URL Shortener Analytics
Generates a PDF report of top 10 clicked short URLs and sends via email
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
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class DailyReportGenerator:
    """Generate and email daily analytics report for URL shortener"""
    
    def __init__(self, db_config, email_config):
        """
        Initialize report generator
        
        Args:
            db_config: Dict with database connection parameters
            email_config: Dict with email configuration
        """
        self.db_config = db_config
        self.email_config = email_config
        self.report_filename = f"url_analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    def fetch_top_urls(self, limit=10):
        """
        Fetch top clicked URLs from database
        
        Args:
            limit: Number of top URLs to fetch
            
        Returns:
            List of dictionaries with URL data
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    u.short_code,
                    u.original,
                    COUNT(c.id) as click_count,
                    MAX(c.clicked_at) as last_clicked
                FROM urls u
                LEFT JOIN clicks c ON u.id = c.url_id
                WHERE c.clicked_at >= NOW() - INTERVAL '1 day'
                GROUP BY u.id, u.short_code, u.original
                ORDER BY click_count DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
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
        print(f"PDF generated: {self.report_filename}")
    
    def send_email(self):
        """Send the generated PDF report via email"""
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
            print(f"Error attaching PDF: {e}")
            return False
        
        # Send email
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"Email sent successfully to {self.email_config['to_email']}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def generate_and_send_report(self):
        """Main method to generate report and send via email"""
        print("Fetching top URLs data...")
        data = self.fetch_top_urls(limit=10)
        
        if not data:
            print("No data available for report generation")
            return False
        
        print(f"Generating PDF report with {len(data)} entries...")
        self.generate_pdf(data)
        
        print("Sending email...")
        success = self.send_email()
        
        # Cleanup
        if os.path.exists(self.report_filename):
            os.remove(self.report_filename)
            print("Temporary PDF file cleaned up")
        
        return success


def main():
    """Main execution function"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME', 'url_shortener'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    # Email configuration
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'from_email': os.getenv('FROM_EMAIL', '[email protected]'),
        'to_email': os.getenv('TO_EMAIL', '[email protected]'),
        'username': os.getenv('EMAIL_USERNAME', '[email protected]'),
        'password': os.getenv('EMAIL_PASSWORD', 'your_password')
    }
    
    # Generate and send report
    generator = DailyReportGenerator(db_config, email_config)
    success = generator.generate_and_send_report()
    
    if success:
        print("Daily report generated and sent successfully!")
    else:
        print("Failed to generate or send daily report")

if __name__ == "__main__":
    main()

