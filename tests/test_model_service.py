"""
Unit tests for the deep learning model service, image preprocessing,
and HAM10000 7-class inference pipeline.
"""
import io
import pytest
from PIL import Image
from services.model_service import (
    get_loaded_model,
    analyze_skin_lesion,
    validate_and_inspect_image,
    check_model_availability,
    HAM10000_CLASSES_7
)

def test_model_availability():
    """
    Verify that check_model_availability detects the trained model file.
    """
    status = check_model_availability()
    assert status['available'] is True
    assert "Genuine" in status['message']

def test_model_inference_pipeline_7class():
    """
    Verify genuine TensorFlow neural network inference on a synthetic test lesion image.
    Ensures correct 224x224 RGB processing, 7-class output format, and probability consistency.
    """
    model = get_loaded_model()
    assert model is not None, "Trained TensorFlow/Keras model failed to load from ml_models/."

    # Create synthetic dermoscopic test image
    img = Image.new('RGB', (224, 224), color=(210, 180, 160))
    metadata = {
        'width': 224,
        'height': 224,
        'aspect_ratio': 1.0,
        'avg_brightness': 183.3,
        'format': 'JPEG'
    }

    result = analyze_skin_lesion(img, metadata, force_demo=False)

    # Assert genuine model execution
    assert result['result_status'] == 'genuine_model'
    assert result['is_demo'] == 0
    assert result['confidence_score'] is not None
    assert 0.0 <= result['confidence_score'] <= 100.0
    assert result['classification'] is not None

    # Assert 7-class probabilities distribution
    all_scores = result['all_class_scores']
    assert all_scores is not None
    assert len(all_scores) == 7

    # Ensure all 7 HAM10000 class codes are present
    returned_codes = {item['code'] for item in all_scores}
    assert returned_codes == set(HAM10000_CLASSES_7)

    # Probabilities should sum to approximately 100%
    total_prob = sum(item['probability'] for item in all_scores)
    assert 99.0 <= total_prob <= 101.0

    # Ensure mandatory educational research disclaimer is included in explanation
    assert "educational AI research prototype" in result['explanation']

def test_validate_and_inspect_image():
    """
    Verify strict image validation logic for formats, dimensions, and corrupt data.
    """
    # 1. Valid RGB image
    valid_img = Image.new('RGB', (300, 300), color=(200, 150, 120))
    buffer = io.BytesIO()
    valid_img.save(buffer, format='JPEG')
    buffer.seek(0)

    is_valid, err, _, meta = validate_and_inspect_image(buffer, 'test_lesion.jpg')
    assert is_valid is True
    assert err is None
    assert meta['width'] == 300
    assert meta['height'] == 300
    assert meta['channels'] == 3

    # 2. Too small image (< 50x50)
    small_img = Image.new('RGB', (30, 30), color=(200, 150, 120))
    buf_small = io.BytesIO()
    small_img.save(buf_small, format='PNG')
    buf_small.seek(0)

    is_valid_small, err_small, _, _ = validate_and_inspect_image(buf_small, 'tiny.png')
    assert is_valid_small is False
    assert "too small" in err_small

    # 3. Corrupted / Non-image bytes
    corrupt_buf = io.BytesIO(b"NOT_AN_IMAGE_FILE_DATA_CORRUPT")
    is_valid_corrupt, err_corrupt, _, _ = validate_and_inspect_image(corrupt_buf, 'corrupt.jpg')
    assert is_valid_corrupt is False
    assert "corrupt" in err_corrupt.lower() or "invalid" in err_corrupt.lower()
