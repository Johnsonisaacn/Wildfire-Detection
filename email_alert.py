import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from datetime import datetime, timedelta
import importlib.util

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_alerts.log'),
        logging.StreamHandler()
        ]
        )

class EmailAlertSystem:
    def __init__(self, config_path='email_config.py'):
        """
        Initialize email alert system with configuration
        """
        self.logger = logging.getLogger('EmailAlerts')
        self.logger.info("EmailAlertSystem initialized")
        self.load_config(config_path)
        self.last_alert_time = None
        
        
        
    def load_config(self, config_path):
        """Load email configuration from file"""
        try:
            # Import the config module
            spec = importlib.util.spec_from_file_location("email_config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            self.config = config_module.EMAIL_CONFIG
            self.logger.info("Email configuration loaded successfully")
            
        except Exception as e:
            # Fallback to environment variables or default config
            self.logger.warning(f"Could not load config file: {e}. Using environment variables.")
            self.config = self.get_config_from_env()
    
    def get_config_from_env(self):
        """Get configuration from environment variables as fallback"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'email_from': os.getenv('EMAIL_FROM', ''),
            'email_password': os.getenv('EMAIL_PASSWORD', ''),
            'email_to': os.getenv('EMAIL_TO', '').split(','),
            'location': os.getenv('LOCATION', 'Unknown Location'),
            'cooldown_minutes': int(os.getenv('COOLDOWN_MINUTES', 5)),
            'subject_prefix': os.getenv('SUBJECT_PREFIX', '🔥 WILDFIRE ALERT - '),
            'emergency_contacts': os.getenv('EMERGENCY_CONTACTS', '')
        }
    
    
    def is_cooldown_active(self):
        """Check if we're in cooldown period to prevent alert spam"""
        if self.last_alert_time is None:
            return False
        
        cooldown_end = self.last_alert_time + timedelta(minutes=self.config['cooldown_minutes'])
        return datetime.now() < cooldown_end
    
    def create_email_content(self, confidence, image_path=None):
        """Create HTML email with alert information"""
        
        html_content = f"""
        <html>
        <body>
            <h2>🚨 WILDFIRE DETECTION ALERT</h2>
            <p><strong>Detection Confidence:</strong> {confidence:.1%}</p>
            <p><strong>Location:</strong> {self.config['location']}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>Emergency Contacts:</h3>
            <p>{self.config['emergency_contacts']}</p>
            
            <hr>
            <p><em>Automated alert from Wildfire Detection System</em></p>
        </body>
        </html>
        """
        
        return html_content
    
    def send_alert(self, confidence, image_path=None, additional_info=None):
        """
        Send wildfire alert email
        """
        # Check cooldown period
        if self.is_cooldown_active():
            self.logger.info("Alert suppressed - cooldown period active")
            return False
        
        try:
            # Create message container - FIXED IMPORTS
            msg = MIMEMultipart()
            msg['Subject'] = f"{self.config['subject_prefix']}Confidence: {confidence:.1%}"
            msg['From'] = self.config['email_from']
            msg['To'] = ', '.join(self.config['email_to'])
            
            # Create HTML body
            html_body = self.create_email_content(confidence, image_path)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                image_attachment = MIMEImage(img_data, name=os.path.basename(image_path))
                msg.attach(image_attachment)
            
            # Send email
            self._send_email(msg)
            
            # Update last alert time
            self.last_alert_time = datetime.now()
            self.logger.info(f"Email alert sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _send_email(self, msg):
        """Internal method to handle SMTP connection and sending"""
        try:
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_from'], self.config['email_password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            raise
    
    def test_connection(self):
        """Test email configuration and connection"""
        try:
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_from'], self.config['email_password'])
            server.quit()
            self.logger.info("Email connection test: SUCCESS")
            return True
        except Exception as e:
            self.logger.error(f"Email connection test: FAILED - {e}")
            return False

