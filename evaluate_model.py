"""
Skin Cancer Detection — Model Evaluation Pipeline on Held-Out Test Split
Evaluates the trained TensorFlow CNN model on unseen test dermoscopy images.
Generates comprehensive classification metrics, confusion matrix, and JSON report.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

import tensorflow as tf
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.preprocessing import label_binarize

CLASSES_7 = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']
CLASS_TO_IDX = {cls: idx for idx, cls in enumerate(CLASSES_7)}
IDX_TO_CLASS = {idx: cls for idx, cls in enumerate(CLASSES_7)}

CLASS_FULL_NAMES = {
    'akiec': 'Actinic Keratoses (akiec)',
    'bcc': 'Basal Cell Carcinoma (bcc)',
    'bkl': 'Benign Keratosis (bkl)',
    'df': 'Dermatofibroma (df)',
    'mel': 'Melanoma (mel)',
    'nv': 'Melanocytic Nevus (nv)',
    'vasc': 'Vascular Lesion (vasc)'
}

def evaluate(model_path="ml_models/skin_cancer_cnn_7class.keras",
             test_csv="ml_models/held_out_test_split.csv",
             output_report="ml_models/evaluation_report.json"):
             
    model_path = Path(model_path)
    if not model_path.exists():
        # Check fallback to skin_cancer_model.h5
        fallback = model_path.parent / "skin_cancer_model.h5"
        if fallback.exists():
            model_path = fallback
        else:
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
    test_csv = Path(test_csv)
    if not test_csv.exists():
        raise FileNotFoundError(f"Held-out test split not found at: {test_csv}")
        
    print(f"[1/4] Loading trained model from {model_path}...")
    model = tf.keras.models.load_model(str(model_path))
    print(f"Model loaded successfully: {model.name}")
    
    print(f"[2/4] Ingesting held-out test records from {test_csv}...")
    df = pd.read_csv(test_csv)
    print(f"Total test instances: {len(df)}")
    
    X_test = []
    y_true = []
    skipped = 0
    
    for _, row in df.iterrows():
        p = Path(row['path'])
        if not p.exists():
            skipped += 1
            continue
        try:
            with Image.open(p) as img:
                img = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
                arr = np.array(img, dtype=np.float32) / 255.0
                X_test.append(arr)
                y_true.append(CLASS_TO_IDX[row['dx']])
        except Exception:
            skipped += 1
            
    if len(X_test) == 0:
        raise ValueError("No valid test images could be loaded from test split!")
        
    X_test = np.array(X_test, dtype=np.float32)
    y_true = np.array(y_true, dtype=np.int32)
    print(f"Verified test images ready for inference: {len(X_test)} (Skipped: {skipped})")
    
    print("[3/4] Performing batch model inference on unseen test set...")
    raw_probs = model.predict(X_test, batch_size=16, verbose=1)
    y_pred = np.argmax(raw_probs, axis=1)
    
    print("[4/4] Computing rigorous classification metrics...")
    acc = accuracy_score(y_true, y_pred)
    
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(CLASSES_7))), zero_division=0
    )
    
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASSES_7))))
    
    # Per-class specificity: True Negatives / (True Negatives + False Positives)
    specificity = []
    for i in range(len(CLASSES_7)):
        tn = np.sum(np.delete(np.delete(cm, i, axis=0), i, axis=1))
        fp = np.sum(cm[:, i]) - cm[i, i]
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        specificity.append(round(spec, 4))
        
    # Multi-class ROC-AUC (one-vs-rest)
    try:
        y_true_bin = label_binarize(y_true, classes=list(range(len(CLASSES_7))))
        roc_auc = float(roc_auc_score(y_true_bin, raw_probs, multi_class='ovr', average='weighted'))
    except Exception:
        roc_auc = None
        
    per_class_metrics = {}
    for i, cls in enumerate(CLASSES_7):
        per_class_metrics[cls] = {
            'class_name': CLASS_FULL_NAMES[cls],
            'support': int(support[i]),
            'precision': round(float(precision[i]), 4),
            'recall_sensitivity': round(float(recall[i]), 4),
            'specificity': specificity[i],
            'f1_score': round(float(f1[i]), 4)
        }
        
    overall_metrics = {
        'test_accuracy': round(float(acc) * 100, 2),
        'macro_precision': round(float(np.mean(precision)), 4),
        'macro_recall': round(float(np.mean(recall)), 4),
        'macro_f1': round(float(np.mean(f1)), 4),
        'weighted_f1': round(float(np.average(f1, weights=support)), 4) if sum(support) > 0 else 0.0,
        'roc_auc_weighted': round(roc_auc, 4) if roc_auc else "N/A",
        'total_test_samples': int(len(y_true))
    }
    
    report_dict = {
        'model_evaluated': str(model_path.name),
        'overall_summary': overall_metrics,
        'per_class_metrics': per_class_metrics,
        'confusion_matrix': cm.tolist(),
        'class_order': CLASSES_7,
        'evaluation_notes': (
            "Held-out test set evaluation on unseen dermoscopic images. "
            "These metrics represent academic research performance on the HAM10000 benchmark, "
            "not verified clinical sensitivity. Biopsy and dermoscopy by a qualified doctor remain mandatory."
        )
    }
    
    # Save JSON report
    out_path = Path(output_report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report_dict, f, indent=2)
    print(f"\nSaved comprehensive evaluation report to: {out_path}")
    
    # Print readable console table
    print("\n" + "="*80)
    print(f" MODEL EVALUATION REPORT ON HELD-OUT TEST DATA ({len(y_true)} Images)")
    print("="*80)
    print(f"Overall Test Accuracy:    {overall_metrics['test_accuracy']}%")
    print(f"Macro F1-Score:           {overall_metrics['macro_f1']}")
    print(f"Weighted F1-Score:        {overall_metrics['weighted_f1']}")
    print(f"ROC-AUC (Weighted OvR):   {overall_metrics['roc_auc_weighted']}")
    print("-" * 80)
    print(f"{'Class':<8} | {'Support':<8} | {'Precision':<10} | {'Recall (Sens)':<13} | {'Specificity':<11} | {'F1-Score':<8}")
    print("-" * 80)
    for cls in CLASSES_7:
        m = per_class_metrics[cls]
        print(f"{cls:<8} | {m['support']:<8} | {m['precision']:<10.4f} | {m['recall_sensitivity']:<13.4f} | {m['specificity']:<11.4f} | {m['f1_score']:<8.4f}")
    print("="*80)
    
    return report_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate trained CNN on held-out test split")
    parser.add_argument("--model", type=str, default="ml_models/skin_cancer_cnn_7class.keras")
    parser.add_argument("--test-csv", type=str, default="ml_models/held_out_test_split.csv")
    parser.add_argument("--output", type=str, default="ml_models/evaluation_report.json")
    args = parser.parse_args()
    
    evaluate(model_path=args.model, test_csv=args.test_csv, output_report=args.output)
