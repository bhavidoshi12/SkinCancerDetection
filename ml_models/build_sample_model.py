"""
Build or export a lightweight CNN model architecture for skin cancer screening demonstration.
Run this script with: python ml_models/build_sample_model.py
"""
import sys
from pathlib import Path

def build_model():
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models
    except ImportError:
        print("TensorFlow is not installed in the active environment.")
        print("Install TensorFlow using: pip install tensorflow")
        return False

    print("Building Skin Lesion Convolutional Neural Network (CNN)...")
    
    # 4-layer CNN Architecture tailored for 224x224 RGB lesion images
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        # Dense Classification Head
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(2, activation='softmax')  # Binary: Benign vs Requires Attention
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    out_dir = Path(__file__).resolve().parent
    model_path = out_dir / 'skin_cancer_model.h5'
    model.save(str(model_path))
    print(f"Model saved successfully to: {model_path}")
    print("Restart the Flask application to enable genuine model inference!")
    return True

if __name__ == '__main__':
    build_model()
