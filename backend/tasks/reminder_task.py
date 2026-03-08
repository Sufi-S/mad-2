from backend.tasks.celery_worker import celery
from backend.services.appointment_service import AppointmentService
from datetime import datetime
import requests
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(name='tasks.send_appointment_reminders')
def send_appointment_reminders():
    """
    Scheduled task to send appointment reminders
    Runs daily at 8 AM
    """
    logger.info("Starting appointment reminders task...")
    
    try:
        # Get appointments for tomorrow
        reminders = AppointmentService.get_upcoming_reminders()
        
        for reminder in reminders:
            # Send Google Chat notification
            send_google_chat_notification.delay(reminder)
            
            # Send email notification
            send_email_notification.delay(reminder)
            
            # Send SMS notification (if implemented)
            # send_sms_notification.delay(reminder)
            
        logger.info(f"Sent {len(reminders)} reminders")
        return f"Processed {len(reminders)} reminders"
        
    except Exception as e:
        logger.error(f"Error in reminder task: {str(e)}")
        raise

@celery.task(name='tasks.send_google_chat_notification')
def send_google_chat_notification(reminder):
    """
    Send reminder via Google Chat webhook
    """
    try:
        # Google Chat webhook URL (configure this in your config)
        webhook_url = "YOUR_GOOGLE_CHAT_WEBHOOK_URL"
        
        message = {
            "text": f"🏥 *Appointment Reminder*\n\n"
                   f"Hello {reminder['patient_name']},\n\n"
                   f"You have an appointment tomorrow at *{reminder['time']}* "
                   f"with Dr. {reminder['doctor_name']}.\n\n"
                   f"Please arrive 15 minutes early.\n\n"
                   f"Thank you for choosing our hospital!"
        }
        
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 200:
            logger.info(f"Google Chat reminder sent to {reminder['patient_name']}")
        else:
            logger.error(f"Google Chat API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending Google Chat notification: {str(e)}")

@celery.task(name='tasks.send_email_notification')
def send_email_notification(reminder):
    """
    Send reminder via email
    """
    try:
        # Email configuration (add to config.py)
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "your-hospital@gmail.com"
        password = "your-app-password"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = reminder['patient_email']
        msg['Subject'] = "Appointment Reminder - Tomorrow"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #333; text-align: center;">🏥 Appointment Reminder</h2>
                
                <p>Dear {reminder['patient_name']},</p>
                
                <p>This is a reminder that you have an appointment scheduled for <strong>tomorrow</strong>.</p>
                
                <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📅 Date:</strong> {reminder['date']}</p>
                    <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {reminder['time']}</p>
                    <p style="margin: 5px 0;"><strong>👨‍⚕️ Doctor:</strong> Dr. {reminder['doctor_name']}</p>
                </div>
                
                <p><strong>Please remember to:</strong></p>
                <ul>
                    <li>Arrive 15 minutes early</li>
                    <li>Bring your ID and insurance card</li>
                    <li>Bring any relevant medical reports</li>
                </ul>
                
                <p style="margin-top: 30px;">Thank you for choosing our hospital!</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #666; font-size: 12px; text-align: center;">
                    To cancel or reschedule, please log in to your account.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email reminder sent to {reminder['patient_email']}")
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")

@celery.task(name='tasks.send_sms_notification')
def send_sms_notification(reminder):
    """
    Send reminder via SMS (using Twilio or similar service)
    """
    try:
        # Example using Twilio
        # from twilio.rest import Client
        
        # account_sid = 'your_account_sid'
        # auth_token = 'your_auth_token'
        # client = Client(account_sid, auth_token)
        
        # message = client.messages.create(
        #     body=f"Reminder: You have an appointment tomorrow at {reminder['time']} with Dr. {reminder['doctor_name']}",
        #     from_='+1234567890',
        #     to=reminder['patient_phone']
        # )
        
        logger.info(f"SMS reminder sent to {reminder['patient_phone']}")
        
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")