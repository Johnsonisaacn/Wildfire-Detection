import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import time
import logging
import os
from datetime import datetime
from model_loader import WildfireModelLoader
from email_alert import EmailAlertSystem

class WildfireDetector:
    def __init__(self, model_path, config_path, email_config_path='email_config.py'):
        # Load model configuration
        with open(config_path, 'r') as f:
            self.model_config = json.load(f)
        
        # Load the optimized model
        self.model = torch.jit.load(model_path)
        self.model.eval()
        
        # Set up image transformations
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self.model_config['input_size']),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.model_config['mean'], std=self.model_config['std'])
        ])
        
        # Initialize email alert system
        self.email_alerts = EmailAlertSystem(email_config_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wildfire_detection.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger()
        
        # Test email connection on startup
        self.logger.info("Testing email connection...")
        if self.email_alerts.test_connection():
            self.logger.info("Email system ready")
        else:
            self.logger.warning("Email system not configured properly")
    
    def predict(self, image):
        """Run inference on captured image"""
        # Preprocess image
        input_tensor = self.transform(image).unsqueeze(0)
        
        # Run prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            probability = output.item()
            prediction = 1 if probability > self.model_config['confidence_threshold'] else 0
        
        return prediction, probability
    
    def process_detection(self, image, image_path=None):
        """
        Process detection and send alerts if fire is detected
        Returns: (is_fire, confidence, alert_sent)
        """
        prediction, confidence = self.predict(image)
        
        if prediction == 1:  # Fire detected
            self.logger.warning(f"🔥 FIRE DETECTED! Confidence: {confidence:.2f}")
            
            # Send email alert
            alert_sent = self.email_alerts.send_alert(
                confidence=confidence,
                image_path=image_path,
                additional_info=f"Auto-detected at {self.email_alerts.config['location']}"
            )
            
            if alert_sent:
                self.logger.info("Email alert sent successfully")
            else:
                self.logger.error("Failed to send email alert")
            
            return True, confidence, alert_sent
        else:
            self.logger.info(f"No fire detected. Confidence: {confidence:.2f}")
            return False, confidence, False
    
    def run_detection_loop(self, capture_function, interval=30):
        """
        Main detection loop
        
        Args:
            capture_function: Function that returns (image, image_path)
            interval: Time between checks in seconds
        """
        self.logger.info("Starting wildfire detection system with email alerts...")
        
        try:
            while True:
                # Capture image using provided function
                image, image_path = capture_function()
                
                # Process detection
                is_fire, confidence, alert_sent = self.process_detection(image, image_path)
                
                if is_fire and alert_sent:
                    # Optional: Add cooldown period after successful alert
                    cooldown = self.email_alerts.config['cooldown_minutes'] * 60
                    self.logger.info(f"Alert sent. Cooling down for {cooldown} seconds...")
                    time.sleep(cooldown)
                else:
                    # Wait for next interval
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            self.logger.info("Detection stopped by user")
        except Exception as e:
            self.logger.error(f"Error in detection loop: {e}")

# Example usage with Pi camera
def pi_camera_capture():
    """Example capture function for Pi camera"""
    from picamera2 import Picamera2
    
    camera = Picamera2()
    camera_config = camera.create_still_configuration(main={"size": (1920, 1080)})
    camera.configure(camera_config)
    camera.start()
    time.sleep(2)
    
    # Capture image
    image_array = camera.capture_array()
    camera.stop()
    
    # Convert to PIL Image
    image = Image.fromarray(image_array)
    
    # Save image with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"capture_{timestamp}.jpg"
    image.save(image_path)
    camera.close()
    
    return image, image_path

if __name__ == "__main__":
    
    # Initialize detector
    detector = WildfireDetector(
        model_path="wildfire_detector_optimized.pt",
        config_path="model_config.json",
        email_config_path="email_config.py"
    )
    
    # Start detection loop
    detector.run_detection_loop(
        capture_function=pi_camera_capture,
        interval=30  # Check every 30 seconds
    )