# email_config.py
"""
Email configuration for wildfire alerts
Create this file and fill in your actual email credentials
"""

EMAIL_CONFIG = {
    # SMTP Server Settings
    'smtp_server': 'smtp.gmail.com',  # For Gmail. For Outlook: 'smtp-mail.outlook.com', Yahoo: 'smtp.mail.yahoo.com'
    'smtp_port': 587,
    
    # Email Account Credentials
    'email_from': 'your.email@gmail.com',  # Your sending email address
    'email_password': 'your_app_password',  # Use App Password for Gmail, not your regular password
    
    # Recipients
    'email_to': [
        'recipient1@email.com',
        'recipient2@email.com'
    ],
    
    # Alert Settings
    'location': 'Remote Outpost Alpha',  # Customize this for each deployment
    'cooldown_minutes': 5,  # Prevent spam - minimum time between alerts
    
    # Email Content
    'subject_prefix': '🔥 WILDFIRE ALERT - ',
    'emergency_contacts': 'Forest Service: 1-800-123-4567, Local Ranger: 1-800-987-6543'
}

# Instructions for setting up Gmail App Password:
"""
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" for mail
4. Use that 16-character password in the config above
"""