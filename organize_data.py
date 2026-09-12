import shutil
import random
from pathlib import Path

random.seed(42)
ROOT = Path(".")
OUT = ROOT / "datasets" / "classify"
KLSG = ROOT / "datasets" / "klsg" / "SeabedObjects-Ship-and-Airplane-dataset-master"
PULSE = ROOT / "datasets" / "marine_pulse"

# Wipe any previous attempt so this script is safe to re-run
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "train").mkdir(parents=True, exist_ok=True)
(OUT / "val").mkdir(parents=True, exist_ok=True)

def split_and_copy(files, class_name):
    files = list(files)
    random.shuffle(files)
    cut = max(1, int(len(files) * 0.8))  # 80% train, 20% val
    train_files, val_files = files[:cut], files[cut:]
    for split, group in [("train", train_files), ("val", val_files)]:
        dest = OUT / split / class_name
        dest.mkdir(parents=True, exist_ok=True)
        for f in group:
            shutil.copy2(f, dest / f.name)
    print(f"{class_name}: {len(train_files)} train, {len(val_files)} val")

# --- KLSG: ships (loose files directly in the folder) ---
ship_files = list(KLSG.glob("ship*.png")) + list(KLSG.glob("ship*.jpg"))
split_and_copy(ship_files, "ship")

# --- KLSG: airplanes (inside plane-real subfolder) ---
plane_files = list((KLSG / "plane-real").glob("*.png")) + list((KLSG / "plane-real").glob("*.jpg"))
split_and_copy(plane_files, "airplane")

# --- Marine-PULSE: already has its own train/test split and class folders ---
name_map = {
    "pipeline or cable": "pipeline_or_cable",
    "engineering platform": "engineering_platform",
    "seabed surface": "seabed_surface",
    "underwater residual mound": "underwater_residual_mound",
}
for src_split, dst_split in [("train", "train"), ("test", "val")]:
    split_dir = PULSE / src_split
    if not split_dir.exists():
        continue
    for class_folder in split_dir.iterdir():
        if class_folder.is_dir() and class_folder.name in name_map:
            dest = OUT / dst_split / name_map[class_folder.name]
            dest.mkdir(parents=True, exist_ok=True)
            imgs = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png"))
            for f in imgs:
                shutil.copy2(f, dest / f.name)
            print(f"{name_map[class_folder.name]} ({dst_split}): {len(imgs)} images")

print("\nDone. Final structure is in datasets/classify/")