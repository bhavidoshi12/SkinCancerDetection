"""
Skin Cancer Detection — Deep Learning CNN Training Pipeline (HAM10000 7-Class)
SVKM's NMIMS MPSTME — Computer Engineering Department
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import MobileNetV2

# HAM10000 7 Diagnostic Categories
CLASSES_7 = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']
CLASS_TO_IDX = {cls: idx for idx, cls in enumerate(CLASSES_7)}
IDX_TO_CLASS = {idx: cls for idx, cls in enumerate(CLASSES_7)}

CLASS_FULL_NAMES = {
    'akiec': 'Actinic Keratoses / Intraepithelial Carcinoma (Pre-cancerous)',
    'bcc': 'Basal Cell Carcinoma (Malignant)',
    'bkl': 'Benign Keratosis-like Lesions (Solar Lentigo / Seborrheic Keratosis)',
    'df': 'Dermatofibroma (Benign)',
    'mel': 'Melanoma (Malignant Skin Cancer)',
    'nv': 'Melanocytic Nevi (Common Benign Mole)',
    'vasc': 'Vascular Lesions (Angioma / Hemorrhage)'
}

def load_and_verify_dataset(metadata_csv, images_dir):
    """
    Reads metadata CSV and verifies existence and integrity of corresponding image files.
    Returns cleaned DataFrame with verified image paths.
    """
    images_dir = Path(images_dir)
    if not os.path.exists(metadata_csv):
        raise FileNotFoundError(f"Metadata file not found: {metadata_csv}")
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
        
    df = pd.read_csv(metadata_csv)
    print(f"[Dataset Ingestion] Total records in metadata: {len(df)}")
    
    verified_rows = []
    missing_count = 0
    corrupt_count = 0
    
    for _, row in df.iterrows():
        img_id = str(row['image_id'])
        # Check for both jpg/png extensions
        img_path = images_dir / f"{img_id}.jpg"
        if not img_path.exists():
            img_path = images_dir / f"{img_id}.png"
            
        if not img_path.exists():
            missing_count += 1
            continue
            
        # Verify image can be opened
        try:
            with Image.open(img_path) as img:
                img.verify()
            verified_rows.append({
                'lesion_id': row.get('lesion_id', img_id),
                'image_id': img_id,
                'dx': row['dx'],
                'path': str(img_path)
            })
        except Exception:
            corrupt_count += 1
            
    verified_df = pd.DataFrame(verified_rows)
    print(f"[Dataset Verification] Verified images available: {len(verified_df)}")
    print(f"  Missing images: {missing_count} | Corrupted files: {corrupt_count}")
    
    # Verify all 7 classes are present
    classes_found = verified_df['dx'].unique().tolist()
    print(f"  Classes present ({len(classes_found)}/7): {classes_found}")
    return verified_df

def create_leakage_free_splits(df, test_size=0.15, val_size=0.15, random_state=42):
    """
    Splits data preventing patient/lesion leakage by grouping on lesion_id.
    Ensures stratified representation across diagnostic classes.
    """
    # Group by lesion_id to determine majority class for each lesion
    lesion_df = df.groupby('lesion_id').agg({
        'dx': 'first',
        'image_id': 'count'
    }).reset_index()
    
    # Split lesions into train+val and test
    train_val_lesions, test_lesions = train_test_split(
        lesion_df,
        test_size=test_size,
        stratify=lesion_df['dx'],
        random_state=random_state
    )
    
    # Split train+val into train and val
    val_ratio = val_size / (1.0 - test_size)
    train_lesions, val_lesions = train_test_split(
        train_val_lesions,
        test_size=val_ratio,
        stratify=train_val_lesions['dx'],
        random_state=random_state
    )
    
    # Map back to image-level DataFrames
    train_df = df[df['lesion_id'].isin(train_lesions['lesion_id'])].copy()
    val_df = df[df['lesion_id'].isin(val_lesions['lesion_id'])].copy()
    test_df = df[df['lesion_id'].isin(test_lesions['lesion_id'])].copy()
    
    print("\n[Data Splitting (Lesion-Grouping)]")
    print(f"  Train set:      {len(train_df)} images ({len(train_lesions)} lesions)")
    print(f"  Validation set: {len(val_df)} images ({len(val_lesions)} lesions)")
    print(f"  Held-out Test:  {len(test_df)} images ({len(test_lesions)} lesions)")
    
    return train_df, val_df, test_df

def build_data_pipeline(df, img_size=(224, 224), batch_size=16, is_training=False):
    """
    Creates an efficient tf.data pipeline with image loading, resizing, normalization,
    and optional training data augmentation.
    """
    paths = df['path'].values
    labels = [CLASS_TO_IDX[dx] for dx in df['dx'].values]
    
    def parse_image(path, label):
        img_bytes = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img_bytes, channels=3)
        img = tf.image.resize(img, img_size, method='bilinear')
        img = tf.cast(img, tf.float32) / 255.0  # Normalized to [0, 1]
        return img, label

    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    dataset = dataset.map(parse_image, num_parallel_calls=tf.data.AUTOTUNE)
    
    if is_training:
        # Data augmentation applied only to training images
        augmentation = keras.Sequential([
            layers.RandomFlip("horizontal_and_vertical"),
            layers.RandomRotation(0.15),
            layers.RandomZoom(0.1),
            layers.RandomBrightness(0.1),
            layers.RandomContrast(0.1)
        ])
        dataset = dataset.shuffle(buffer_size=len(df), reshuffle_each_iteration=True)
        dataset = dataset.batch(batch_size)
        dataset = dataset.map(lambda x, y: (augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
    else:
        dataset = dataset.batch(batch_size)
        
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    return dataset

def build_transfer_learning_model(img_size=(224, 224, 3), num_classes=7):
    """
    Builds a deep CNN using MobileNetV2 with ImageNet transfer learning.
    """
    print("\n[Model Construction] Initializing MobileNetV2 with ImageNet weights...")
    try:
        base_model = MobileNetV2(
            input_shape=img_size,
            include_top=False,
            weights='imagenet'
        )
        print("  Successfully loaded pre-trained ImageNet weights.")
    except Exception as e:
        print(f"  Note: Loading without pre-cached weights ({e}), initializing random weights.")
        base_model = MobileNetV2(
            input_shape=img_size,
            include_top=False,
            weights=None
        )
        
    # Fine-tune the top 20 convolutional layers of MobileNetV2
    base_model.trainable = True
    for layer in base_model.layers[:-25]:
        layer.trainable = False
        
    inputs = layers.Input(shape=img_size, name="input_lesion_tensor")
    x = base_model(inputs)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(128, activation='relu', name="dense_features")(x)
    x = layers.Dropout(0.4, name="dropout_regularization")(x)
    outputs = layers.Dense(num_classes, activation='softmax', name="softmax_probabilities")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="DermaCare_MobileNetV2_7Class")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def train(metadata_csv, images_dir, output_dir="ml_models", epochs=10, batch_size=16):
    start_time = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load and clean dataset
    df = load_and_verify_dataset(metadata_csv, images_dir)
    if len(df) < 20:
        raise ValueError(f"Insufficient images ({len(df)}) for multi-class training.")
        
    # 2. Split dataset
    train_df, val_df, test_df = create_leakage_free_splits(df)
    
    # Save held-out test split for evaluate_model.py
    test_csv_path = output_dir / "held_out_test_split.csv"
    test_df.to_csv(test_csv_path, index=False)
    print(f"Saved held-out test split to: {test_csv_path}")
    
    # 3. Compute class weights to handle imbalance
    train_labels = [CLASS_TO_IDX[dx] for dx in train_df['dx'].values]
    present_classes = np.unique(train_labels)
    weights = compute_class_weight('balanced', classes=present_classes, y=train_labels)
    class_weight_dict = {cls_idx: float(weight) for cls_idx, weight in zip(present_classes, weights)}
    print(f"Computed balanced class weights: {class_weight_dict}")
    
    # 4. Prepare tf.data pipelines
    train_ds = build_data_pipeline(train_df, batch_size=batch_size, is_training=True)
    val_ds = build_data_pipeline(val_df, batch_size=batch_size, is_training=False)
    
    # 5. Build model
    model = build_transfer_learning_model()
    model.summary()
    
    # 6. Callbacks
    best_weights_path = output_dir / "best_model_weights.weights.h5"
    cb_list = [
        callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1
        ),
        callbacks.ModelCheckpoint(
            filepath=str(best_weights_path),
            monitor='val_accuracy',
            save_best_only=True,
            save_weights_only=True,
            verbose=1
        )
    ]
    
    # 7. Training Execution
    print(f"\n[Training] Starting neural network training for {epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        class_weight=class_weight_dict,
        callbacks=cb_list,
        verbose=1
    )
    
    training_duration = round(time.time() - start_time, 2)
    print(f"\nTraining completed in {training_duration} seconds.")
    
    # 8. Save Final Model in Keras native format and H5 format
    model_keras_path = output_dir / "skin_cancer_cnn_7class.keras"
    model_h5_path = output_dir / "skin_cancer_model.h5"
    
    model.save(str(model_keras_path))
    model.save(str(model_h5_path))
    print(f"Saved trained model to: {model_keras_path}")
    print(f"Saved deployment model to: {model_h5_path}")
    
    # 9. Plot and Save Learning Curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(history.history['accuracy'], label='Train Accuracy', color='#657C68', lw=2)
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy', color='#C98F9D', lw=2)
    ax1.set_title('Training & Validation Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(history.history['loss'], label='Train Loss', color='#657C68', lw=2)
    ax2.plot(history.history['val_loss'], label='Val Loss', color='#C98F9D', lw=2)
    ax2.set_title('Training & Validation Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plot_path = output_dir / "training_curves.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"Saved learning curves plot to: {plot_path}")
    
    # 10. Save Model Training Metadata
    final_val_acc = float(history.history['val_accuracy'][-1])
    final_val_loss = float(history.history['val_loss'][-1])
    
    metadata = {
        'model_name': 'DermaCare MobileNetV2 HAM10000 7-Class',
        'architecture': 'MobileNetV2 Transfer Learning',
        'input_shape': [224, 224, 3],
        'normalization': 'pixel / 255.0',
        'classes': CLASSES_7,
        'class_full_names': CLASS_FULL_NAMES,
        'class_to_idx': CLASS_TO_IDX,
        'idx_to_class': IDX_TO_CLASS,
        'dataset': 'HAM10000 & ISIC Archive',
        'total_images_used': len(df),
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'epochs_completed': len(history.history['accuracy']),
        'training_duration_seconds': training_duration,
        'final_val_accuracy': round(final_val_acc * 100, 2),
        'final_val_loss': round(final_val_loss, 4),
        'created_at': time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        'disclaimer': 'Research prototype. Not for clinical diagnosis.'
    }
    
    metadata_json_path = output_dir / "model_metadata.json"
    with open(metadata_json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata JSON to: {metadata_json_path}")
    
    return model, metadata

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train CNN model on HAM10000 dataset")
    parser.add_argument("--metadata", type=str, default="dataset/HAM10000_subset_metadata.csv")
    parser.add_argument("--images-dir", type=str, default="dataset/images")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--output-dir", type=str, default="ml_models")
    args = parser.parse_args()
    
    train(
        metadata_csv=args.metadata,
        images_dir=args.images_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
