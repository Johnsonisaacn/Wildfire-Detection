import smtplib
import logging
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from email.mime.image import MimeImage
from email.mime.application import MimeApplication
import os
from datetime import datetime, timedelta
import json

class EmailAlertSystem:
    def __init__(self, config_path='email_config.py'):
        """
        Initialize email alert system with configuration
        
        Args:
            config_path: Path to email configuration file
        """
        self.load_config(config_path)
        self.last_alert_time = None
        self.setup_logging()
        
    def load_config(self, config_path):
        """Load email configuration from file"""
        try:
            # Import the config module
            import importlib.util
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
    
    def setup_logging(self):
        """Setup logging for email alerts"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_alerts.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('EmailAlerts')
    
    def is_cooldown_active(self):
        """Check if we're in cooldown period to prevent alert spam"""
        if self.last_alert_time is None:
            return False
        
        cooldown_end = self.last_alert_time + timedelta(minutes=self.config['cooldown_minutes'])
        return datetime.now() < cooldown_end
    
    def create_email_content(self, confidence, image_path=None):
        """Create HTML email with alert information"""
        
        # HTML template for the email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert {{ background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; }}
                .confidence {{ color: #d32f2f; font-weight: bold; font-size: 18px; }}
                .info {{ background-color: #e3f2fd; padding: 10px; border-radius: 5px; }}
                .contacts {{ background-color: #fff3e0; padding: 10px; border-radius: 5px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h2>🚨 WILDFIRE DETECTION ALERT</h2>
                <p class="confidence">Detection Confidence: {confidence:.1%}</p>
            </div>
            
            <div class="info">
                <h3>Alert Details:</h3>
                <ul>
                    <li><strong>Location:</strong> {self.config['location']}</li>
                    <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li><strong>System:</strong> Raspberry Pi Wildfire Detection</li>
                </ul>
            </div>
            
            <div class="contacts">
                <h3>🚒 Emergency Contacts:</h3>
                <p>{self.config['emergency_contacts']}</p>
            </div>
            
            <div>
                <h3>📋 Required Actions:</h3>
                <ol>
                    <li>Verify the attached image</li>
                    <li>Contact local authorities if confirmed</li>
                    <li>Check for additional alerts from the system</li>
                    <li>Monitor the situation closely</li>
                </ol>
            </div>
            
            <hr>
            <p><em>This is an automated alert from the Wildfire Detection System. 
            Please verify all information before taking action.</em></p>
        </body>
        </html>
        """
        
        return html_content
    
    def send_alert(self, confidence, image_path=None, additional_info=None):
        """
        Send wildfire alert email
        
        Args:
            confidence: Detection confidence (0.0 to 1.0)
            image_path: Path to the alert image
            additional_info: Any additional information about the detection
        """
        
        # Check cooldown period
        if self.is_cooldown_active():
            self.logger.info("Alert suppressed - cooldown period active")
            return False
        
        try:
            # Create message container
            msg = MimeMultipart()
            msg['Subject'] = f"{self.config['subject_prefix']}Confidence: {confidence:.1%} - {self.config['location']}"
            msg['From'] = self.config['email_from']
            msg['To'] = ', '.join(self.config['email_to'])
            
            # Create HTML body
            html_body = self.create_email_content(confidence, image_path)
            if additional_info:
                html_body += f"<p><strong>Additional Info:</strong> {additional_info}</p>"
            
            msg.attach(MimeText(html_body, 'html'))
            
            # Attach image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                image_attachment = MimeImage(img_data, name=os.path.basename(image_path))
                msg.attach(image_attachment)
            
            # Send email
            self._send_email(msg)
            
            # Update last alert time
            self.last_alert_time = datetime.now()
            self.logger.info(f"Email alert sent successfully to {len(self.config['email_to'])} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _send_email(self, msg):
        """Internal method to handle SMTP connection and sending"""
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            
            # Login to email account
            server.login(self.config['email_from'], self.config['email_password'])
            
            # Send email
            server.send_message(msg)
            
            # Close connection
            server.quit()
            
        except smtplib.SMTPAuthenticationError:
            self.logger.error("SMTP Authentication failed. Check your email and password.")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error occurred: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}")
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

# Utility function to create config file
def create_email_config_template():
    """Create a template email configuration file"""
    template = '''# email_config.py
"""
Email configuration for wildfire alerts
Fill in your actual email credentials
"""

EMAIL_CONFIG = {
    # SMTP Server Settings
    'smtp_server': 'smtp.gmail.com',  # For Gmail. For Outlook: 'smtp-mail.outlook.com'
    'smtp_port': 587,
    
    # Email Account Credentials
    'email_from': 'your.email@gmail.com',  # Your sending email address
    'email_password': 'your_app_password',  # Use App Password for Gmail
    
    # Recipients (comma-separated list)
    'email_to': [
        'recipient1@email.com',
        'recipient2@email.com'
    ],
    
    # Alert Settings
    'location': 'Remote Outpost Alpha',
    'cooldown_minutes': 5,
    
    # Email Content
    'subject_prefix': '🔥 WILDFIRE ALERT - ',
    'emergency_contacts': 'Forest Service: 1-800-123-4567, Local Ranger: 1-800-987-6543'
}
'''
    
    with open('email_config.py', 'w') as f:
        f.write(template)
    
    print("Email config template created. Please edit 'email_config.py' with your credentials.")