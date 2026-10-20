# Skin Cancer Detection — Deep Learning Model Specifications

This directory contains the machine learning integration specifications for the **Skin Cancer Detection System** (College Mini-Project, SVKM's NMIMS MPSTME).

---

## 1. Core Model Specifications

- **Architecture:** Convolutional Neural Network (CNN) / Transfer Learning (MobileNetV2, ResNet50, or EfficientNet)
- **Input Dimensions:** `(224, 224, 3)` (RGB, 3 color channels)
- **Input Preprocessing:** Bilinear interpolation resizing to 224x224, pixel scaling normalized to `[0.0, 1.0]` (`x / 255.0`).
- **File Format:** HDF5 (`.h5`) or Keras Native Archive (`.keras`).
- **Target File Path:** `ml_models/skin_cancer_model.h5` or `ml_models/skin_cancer_model.keras`

---

## 2. Benchmark Datasets & Class Mappings

The system supports both 7-class HAM10000 classification and binary risk screening:

### Option A: Standard HAM10000 7-Class Scheme
1. `akiec` — Actinic Keratoses and Intraepithelial Carcinoma (Pre-cancerous)
2. `bcc` — Basal Cell Carcinoma (Malignant)
3. `bkl` — Benign Keratosis-like Lesions (Benign)
4. `df` — Dermatofibroma (Benign)
5. `mel` — Melanoma (Malignant)
6. `nv` — Melanocytic Nevi (Benign Mole)
7. `vasc` — Vascular Lesions (Benign)

### Option B: Binary Screening Scheme
1. Class 0: `Benign Lesion`
2. Class 1: `Potentially Malignant / Requires Attention`

---

## 3. How to Connect a Trained Model

1. Train your model using TensorFlow/Keras on the HAM10000 or ISIC dataset.
2. Save your trained model:
   ```python
   model.save("ml_models/skin_cancer_model.h5")
   ```
3. Restart or refresh the Flask web application.
4. The system will automatically detect the file, initialize the inference pipeline, and transition from **Demo Mode** to **Genuine AI Active** on the dashboard and results pages.

---

## 4. Medical Safety & Demo Mode Protocol

If no model weights file is present in this directory:
- The web application executes in **Demo / Educational Mode**.
- In strict adherence to clinical safety standards, **it never fabricates fake random probabilities or presents simulated guesses as genuine AI predictions**.
- Users can test file upload validation, spatial image metrics (resolution, aspect ratio, contrast), and explore verified HAM10000 educational reference benchmark study cases.
