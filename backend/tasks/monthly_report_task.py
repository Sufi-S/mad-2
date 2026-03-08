from backend.tasks.celery_worker import celery
from backend.services.report_service import ReportService
from backend.models.doctor_model import Doctor
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import io

logger = logging.getLogger(__name__)

@celery.task(name='tasks.generate_monthly_reports')
def generate_monthly_reports():
    """
    Generate monthly activity reports for all doctors
    Runs on the 1st of every month at 9 AM
    """
    logger.info("Starting monthly report generation...")
    
    try:
        # Get current date
        today = datetime.now()
        last_month = today - timedelta(days=30)
        
        # Get all doctors
        doctors = Doctor.query.all()
        
        for doctor in doctors:
            # Generate report for each doctor
            generate_doctor_report.delay(
                doctor.id,
                last_month.year,
                last_month.month
            )
        
        logger.info(f"Queued {len(doctors)} monthly reports")
        return f"Queued {len(doctors)} reports"
        
    except Exception as e:
        logger.error(f"Error in monthly report task: {str(e)}")
        raise

@celery.task(name='tasks.generate_doctor_report')
def generate_doctor_report(doctor_id, year, month):
    """
    Generate and send monthly report for a specific doctor
    """
    try:
        # Generate HTML report
        html_report, error = ReportService.generate_monthly_doctor_report(
            doctor_id, year, month
        )
        
        if error:
            logger.error(f"Error generating report for doctor {doctor_id}: {error}")
            return
        
        # Get doctor details
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            logger.error(f"Doctor {doctor_id} not found")
            return
        
        # Send report via email
        send_report_email.delay(
            doctor.user.email,
            doctor.name,
            html_report,
            year,
            month
        )
        
        logger.info(f"Report generated for Dr. {doctor.name}")
        
    except Exception as e:
        logger.error(f"Error in generate_doctor_report: {str(e)}")

@celery.task(name='tasks.send_report_email')
def send_report_email(doctor_email, doctor_name, html_report, year, month):
    """
    Send monthly report via email
    """
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "your-hospital@gmail.com"
        password = "your-app-password"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = doctor_email
        msg['Subject'] = f"Monthly Activity Report - {month}/{year}"
        
        # Attach HTML content
        msg.attach(MIMEText(html_report, 'html'))
        
        # Also create PDF version (optional)
        # pdf_buffer = create_pdf_report(html_report)
        # if pdf_buffer:
        #     part = MIMEBase('application', 'pdf')
        #     part.set_payload(pdf_buffer.getvalue())
        #     encoders.encode_base64(part)
        #     part.add_header(
        #         'Content-Disposition',
        #         f'attachment; filename=report_{month}_{year}.pdf'
        #     )
        #     msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Monthly report sent to Dr. {doctor_name}")
        
    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")

def create_pdf_report(html_content):
    """
    Convert HTML report to PDF (optional feature)
    """
    try:
        # Using weasyprint or pdfkit
        # import pdfkit
        # pdf = pdfkit.from_string(html_content, False)
        # return io.BytesIO(pdf)
        pass
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        return None