from email_alert import EmailAlertSystem, create_email_config_template
import os

def test_email_system():
    """Test the email alert system"""
    
    if not os.path.exists('email_config.py'):
        print("Creating email config template...")
        create_email_config_template()
        print("Please edit email_config.py with your credentials and run this script again.")
        return
    
    print("Testing email alert system...")
    
    # Initialize email system
    email_system = EmailAlertSystem('email_config.py')
    
    # Test connection
    print("1. Testing SMTP connection...")
    if email_system.test_connection():
        print("   ✅ Connection successful!")
    else:
        print("   ❌ Connection failed. Check your credentials.")
        return
    
    # Send test alert
    print("2. Sending test alert...")
    success = email_system.send_alert(
        confidence=0.85,
        image_path=None,  # No image for test
        additional_info="This is a test alert from the wildfire detection system."
    )
    
    if success:
        print("   ✅ Test alert sent successfully!")
        print("   Check your email inbox for the test message.")
    else:
        print("   ❌ Failed to send test alert.")

if __name__ == "__main__":
    test_email_system()