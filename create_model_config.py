# create_model_config.py
import json

# Create the model configuration
model_config = {
    'input_size': 224,
    'mean': [0.485, 0.456, 0.406],
    'std': [0.229, 0.224, 0.225],
    'class_names': ['nofire', 'fire'],
    'confidence_threshold': 0.7,  
    'model_type': 'mobilenet_v2_binary',
    'trained_date': '2025-09-28'
}

# Save to file
with open('model_config.json', 'w') as f:
    json.dump(model_config, f, indent=2)

print("model_config.json created successfully!")