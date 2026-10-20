import os
import json
from pathlib import Path
from PIL import Image, ImageStat
import numpy as np
from config import Config

# Safe optional import of TensorFlow
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except (ImportError, Exception):
    tf = None
    TF_AVAILABLE = False

_CACHED_MODEL = None
_CACHED_METADATA = None

HAM10000_CLASSES_7 = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

CLASS_FULL_NAMES = {
    'akiec': 'Actinic Keratoses / Intraepithelial Carcinoma (Pre-cancerous)',
    'bcc': 'Basal Cell Carcinoma (Malignant Non-Melanoma)',
    'bkl': 'Benign Keratosis-like Lesions (Solar Lentigo / Seborrheic Keratosis)',
    'df': 'Dermatofibroma (Benign)',
    'mel': 'Melanoma (Malignant Skin Cancer)',
    'nv': 'Melanocytic Nevi (Common Benign Mole)',
    'vasc': 'Vascular Lesions (Angioma / Hemorrhage)'
}

MALIGNANT_CLASSES = {'mel', 'bcc', 'akiec'}

def check_model_availability():
    """
    Check if a genuine TensorFlow/Keras model is installed and ready.
    Prioritizes skin_cancer_cnn_7class.keras or skin_cancer_model.h5 in ml_models/.
    """
    keras_path = Config.MODEL_DIR / 'skin_cancer_cnn_7class.keras'
    h5_path = Config.MODEL_DIR / 'skin_cancer_model.h5'
    fallback_keras = Config.MODEL_DIR / 'skin_cancer_model.keras'
    
    found_path = None
    if keras_path.exists():
        found_path = keras_path
    elif h5_path.exists():
        found_path = h5_path
    elif fallback_keras.exists():
        found_path = fallback_keras
        
    if not TF_AVAILABLE:
        return {
            'available': False,
            'tf_installed': False,
            'model_path': str(found_path) if found_path else None,
            'message': 'TensorFlow is not installed in the active environment.'
        }
        
    if not found_path:
        return {
            'available': False,
            'tf_installed': True,
            'model_path': None,
            'message': 'Trained model file not found in ml_models/. Please run: python train_model.py'
        }
        
    return {
        'available': True,
        'tf_installed': True,
        'model_path': str(found_path),
        'message': f'Genuine TensorFlow CNN model loaded from {found_path.name}.'
    }

def get_loaded_model():
    """
    Lazily loads and caches the TensorFlow model in memory.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL
        
    status = check_model_availability()
    if not status['available']:
        return None
        
    try:
        _CACHED_MODEL = tf.keras.models.load_model(status['model_path'])
        return _CACHED_MODEL
    except Exception as e:
        print(f"Error loading trained model from {status['model_path']}: {e}")
        return None

def get_model_metadata():
    """
    Loads training metadata JSON if present.
    """
    global _CACHED_METADATA
    if _CACHED_METADATA is not None:
        return _CACHED_METADATA
        
    meta_path = Config.MODEL_DIR / "model_metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r') as f:
                _CACHED_METADATA = json.load(f)
                return _CACHED_METADATA
        except Exception:
            pass
    return None

def validate_and_inspect_image(file_stream, filename):
    """
    Strictly validates image format, resolution, and decodability.
    Rejects non-image files, corrupted data, or oversized files.
    """
    if not filename:
        return False, "No file was selected.", None, {}
        
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return False, f"Unsupported file format (.{ext}). Only JPG, JPEG, and PNG files are allowed.", None, {}
        
    try:
        image = Image.open(file_stream)
        image.verify()
        
        file_stream.seek(0)
        image = Image.open(file_stream)
        image = image.convert('RGB')
    except Exception:
        return False, "The uploaded file is corrupt, invalid, or not a recognizable image file.", None, {}
        
    width, height = image.size
    if width < 50 or height < 50:
        return False, f"Image resolution ({width}x{height}) is too small. Please provide an image of at least 50x50 pixels.", None, {}
        
    if width > 6000 or height > 6000:
        return False, f"Image resolution ({width}x{height}) exceeds maximum permissible dimensions (6000x6000).", None, {}
        
    stat = ImageStat.Stat(image)
    avg_brightness = sum(stat.mean[:3]) / 3.0
    color_std_dev = sum(stat.stddev[:3]) / 3.0
    
    metadata = {
        'width': width,
        'height': height,
        'aspect_ratio': round(width / height, 2),
        'avg_brightness': round(avg_brightness, 1),
        'contrast_metric': round(color_std_dev, 1),
        'channels': 3,
        'format': ext.upper()
    }
    
    return True, None, image, metadata

def analyze_skin_lesion(image, metadata, force_demo=False):
    """
    Executes genuine neural network inference using the trained TensorFlow model.
    Applies exact training preprocessing (224x224 RGB, normalized to [0, 1]).
    Never fabricates random numbers or fake confidence scores.
    """
    status = check_model_availability()
    model = None if force_demo else get_loaded_model()
    
    if model is None or force_demo:
        # Transparent model unavailable state
        return {
            'result_status': 'unavailable' if not force_demo else 'demo_simulation',
            'classification': 'Model Unavailable — Real Inference Offline',
            'confidence_score': None,
            'explanation': (
                "MODEL UNAVAILABLE: No trained TensorFlow deep learning model could be loaded from ml_models/. "
                "In strict compliance with medical software safety guidelines, simulated probabilities or fabricated guesses are never generated. "
                "To train and deploy a genuine model, execute: 'python train_model.py'."
            ),
            'is_demo': 1 if force_demo else 0,
            'model_version': 'Engine Offline',
            'all_class_scores': None
        }
        
    try:
        # Preprocess matching training pipeline exactly
        resized = image.resize((224, 224), Image.Resampling.BILINEAR)
        img_array = np.array(resized, dtype=np.float32) / 255.0
        input_tensor = np.expand_dims(img_array, axis=0)
        
        # Genuine neural network inference
        raw_predictions = model.predict(input_tensor, verbose=0)[0]
        
        num_classes = len(raw_predictions)
        if num_classes == 7:
            classes = HAM10000_CLASSES_7
        else:
            classes = [f"Class_{i}" for i in range(num_classes)]
            
        pred_index = int(np.argmax(raw_predictions))
        top_code = classes[pred_index] if pred_index < len(classes) else f"Class_{pred_index}"
        top_label = CLASS_FULL_NAMES.get(top_code, top_code)
        confidence = float(raw_predictions[pred_index]) * 100.0
        
        # Build all 7 class output probabilities
        all_scores = []
        for i in range(len(raw_predictions)):
            code = classes[i] if i < len(classes) else f"Class_{i}"
            label = CLASS_FULL_NAMES.get(code, code)
            prob = float(raw_predictions[i]) * 100.0
            all_scores.append({
                'code': code,
                'label': label,
                'probability': round(prob, 2),
                'is_concerning': code in MALIGNANT_CLASSES
            })
            
        all_scores.sort(key=lambda x: x['probability'], reverse=True)
        
        # Responsible clinical interpretation narrative
        is_concerning = top_code in MALIGNANT_CLASSES
        if is_concerning:
            risk_note = (
                f"The deep learning neural network identified features statistically aligned with '{top_label}'. "
                "This category warrants prompt, formal evaluation by a licensed dermatologist for dermoscopic examination and potential biopsy."
            )
        else:
            risk_note = (
                f"The deep learning neural network identified morphological patterns characteristic of '{top_label}'. "
                "Even when predicted as benign, AI predictions cannot rule out malignancy. Continue periodic self-monitoring under the ABCDE criteria."
            )
            
        disclaimer_note = (
            " IMPORTANT CLINICAL NOTICE: This project is an educational AI research prototype. "
            "Its predictions are not a medical diagnosis and have not been established as clinically reliable. "
            "Consult a qualified dermatologist for assessment of concerning or changing skin lesions."
        )
        
        return {
            'result_status': 'genuine_model',
            'classification': top_label,
            'confidence_score': round(confidence, 2),
            'explanation': risk_note + disclaimer_note,
            'is_demo': 0,
            'model_version': 'MobileNetV2-HAM10000-v2.0',
            'all_class_scores': all_scores
        }
    except Exception as e:
        print(f"Error during neural inference: {e}")
        return {
            'result_status': 'unavailable',
            'classification': 'Inference Error',
            'confidence_score': None,
            'explanation': f"An unexpected error occurred during deep learning inference: {e}",
            'is_demo': 0,
            'model_version': 'Error',
            'all_class_scores': None
        }

def get_educational_sample_records():
    """
    Returns reference benchmark cases for educational UI demonstration.
    """
    return [
        {
            'sample_id': 'HAM_BENIGN_01',
            'title': 'HAM10000 Reference: Melanocytic Nevus (ISIC_0024306)',
            'classification': 'Melanocytic Nevi (nv) — Common Benign Mole',
            'confidence_score': 94.20,
            'is_demo': 1,
            'result_status': 'demo_simulation',
            'explanation': 'EDUCATIONAL BENCHMARK SAMPLE: Reference study from the HAM10000 dataset illustrating a typical benign melanocytic nevus with symmetric pigmentation.',
            'category': 'Benign'
        },
        {
            'sample_id': 'HAM_MELANOMA_02',
            'title': 'HAM10000 Reference: Superficial Melanoma (ISIC_0029314)',
            'classification': 'Melanoma (mel) — Malignant Skin Cancer',
            'confidence_score': 88.70,
            'is_demo': 1,
            'result_status': 'demo_simulation',
            'explanation': 'EDUCATIONAL BENCHMARK SAMPLE: Reference study illustrating superficial spreading melanoma with asymmetric architecture and pigment variegation.',
            'category': 'Requires Attention'
        }
    ]
