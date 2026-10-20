"""
HAM10000 Dataset Downloader
Fetches the official HAM10000 metadata CSV and downloads genuine dermoscopic images
from the official ISIC Archive S3 storage.
"""

import os
import sys
import argparse
import requests
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

METADATA_URL = "https://raw.githubusercontent.com/uyxela/Skin-Lesion-Classifier/master/HAM10000_metadata.csv"
S3_THUMBNAIL_BASE = "https://isic-archive.s3.amazonaws.com/thumbnails/{image_id}_thumbnail.jpg"
S3_IMAGE_BASE = "https://isic-archive.s3.amazonaws.com/images/{image_id}.jpg"

CLASSES_7 = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

def download_file(url, dest_path):
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        return True, dest_path.name, "already exists"
        
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and len(r.content) > 500:
            dest_path.write_bytes(r.content)
            return True, dest_path.name, "downloaded"
        else:
            return False, dest_path.name, f"HTTP {r.status_code}"
    except Exception as e:
        return False, dest_path.name, str(e)

def setup_dataset(target_dir="dataset", samples_per_class=60, use_thumbnails=True):
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    images_dir = target_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_path = target_path / "HAM10000_metadata.csv"
    print(f"[1/3] Checking HAM10000 metadata at {metadata_path}...")
    if not metadata_path.exists():
        print(f"Downloading official HAM10000 metadata from: {METADATA_URL}")
        r = requests.get(METADATA_URL)
        if r.status_code == 200:
            metadata_path.write_bytes(r.content)
            print(f"Metadata saved successfully ({len(r.content)} bytes).")
        else:
            raise RuntimeError(f"Failed to download metadata: HTTP {r.status_code}")
    else:
        print("Metadata CSV already present.")
        
    df = pd.read_csv(metadata_path)
    print(f"Loaded metadata: {len(df)} records across 7 diagnostic classes.")
    print("Class distribution in full metadata:")
    for cls in CLASSES_7:
        print(f"  - {cls:6s}: {sum(df['dx'] == cls)}")
        
    print(f"\n[2/3] Selecting balanced stratified subset ({samples_per_class} per class)...")
    sampled_dfs = []
    for cls in CLASSES_7:
        cls_df = df[df['dx'] == cls]
        # Group by lesion_id first to ensure lesion-level independence
        unique_lesions = cls_df['lesion_id'].unique()
        selected_lesions = unique_lesions[:min(samples_per_class, len(unique_lesions))]
        sampled_subset = cls_df[cls_df['lesion_id'].isin(selected_lesions)].copy()
        if len(sampled_subset) > samples_per_class:
            sampled_subset = sampled_subset.head(samples_per_class)
        sampled_dfs.append(sampled_subset)
        print(f"  Selected {len(sampled_subset)} images for class '{cls}'")
        
    sampled_df = pd.concat(sampled_dfs).drop_duplicates(subset=['image_id']).reset_index(drop=True)
    subset_csv_path = target_path / "HAM10000_subset_metadata.csv"
    sampled_df.to_csv(subset_csv_path, index=False)
    print(f"Stratified subset metadata saved to: {subset_csv_path} ({len(sampled_df)} images total)")
    
    print(f"\n[3/3] Downloading {len(sampled_df)} real dermoscopic images from official ISIC repository...")
    download_tasks = []
    for _, row in sampled_df.iterrows():
        img_id = row['image_id']
        dest = images_dir / f"{img_id}.jpg"
        url = S3_THUMBNAIL_BASE.format(image_id=img_id) if use_thumbnails else S3_IMAGE_BASE.format(image_id=img_id)
        download_tasks.append((url, dest))
        
    successful = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_file, url, dest): dest.name for url, dest in download_tasks}
        for future in as_completed(futures):
            success, name, status = future.result()
            if success:
                successful += 1
                if successful % 50 == 0 or successful == len(download_tasks):
                    print(f"  Progress: {successful}/{len(download_tasks)} images ready...")
            else:
                print(f"  Warning: {name} failed: {status}")
                
    print(f"\nDataset download complete! {successful}/{len(download_tasks)} genuine images available in {images_dir}")
    return subset_csv_path, images_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download HAM10000 dataset subset")
    parser.add_argument("--samples", type=int, default=50, help="Number of images per diagnostic class (default: 50)")
    parser.add_argument("--dir", type=str, default="dataset", help="Target dataset directory")
    args = parser.parse_args()
    
    setup_dataset(target_dir=args.dir, samples_per_class=args.samples)
