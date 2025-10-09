#!/bin/bash
# setup_pi.sh

echo "Setting up email alerts for wildfire detection..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and required packages
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies for OpenCV
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

# Create virtual environment
python3 -m venv wildfire_env
source wildfire_env/bin/activate

# Install Python packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install opencv-python-headless pillow requests smtplib
pip install picamera2  # For Pi camera

python3 -c "from email_alert import create_email_config_template; create_email_config_template()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📧 Next steps:"
echo "1. Edit email_config.py with your email credentials"
echo "2. Test the system with: python3 test_email_alerts.py"
echo "3. Run the detector: python3 wildfire_detector_with_email.py"

echo "Setup complete! Activate virtual environment with: source wildfire_env/bin/activate"