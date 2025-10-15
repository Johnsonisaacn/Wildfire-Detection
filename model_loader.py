import torch
import torch.nn as nn
from torchvision import models
import json
import logging

class WildfireModelLoader:
    def __init__(self):
        self.logger = logging.getLogger('ModelLoader')
    
    def create_model_architecture(self, num_classes=1):
        """Create the same model architecture used during training"""
        model = models.mobilenet_v2(weights=None)  # No pre-trained weights
        
        # Replace classifier for binary classification
        model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(model.last_channel, num_classes),
            nn.Sigmoid()
        )
        return model
    
    def load_model(self, model_path, config_path):
        """Load model with error handling"""
        try:
            # Load model configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Try different loading methods
            try:
                # Method 1: Direct load (for .pth files)
                if model_path.endswith('.pth'):
                    model = self.create_model_architecture()
                    model.load_state_dict(torch.load(model_path, map_location='cpu'))
                    model.eval()
                    self.logger.info("Model loaded successfully using state_dict")
                    return model, config
                    
            except Exception as e:
                self.logger.warning(f"Method 1 failed: {e}")
            
            try:
                # Method 2: Try loading entire model
                model = torch.load(model_path, map_location='cpu')
                if isinstance(model, torch.jit.ScriptModule):
                    self.logger.info("Model loaded as TorchScript")
                else:
                    model.eval()
                    self.logger.info("Model loaded as full model object")
                return model, config
                
            except Exception as e:
                self.logger.warning(f"Method 2 failed: {e}")
            
            # If all methods fail
            raise Exception(f"Could not load model {model_path}. All loading methods failed.")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise