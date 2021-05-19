#!/usr/bin/env python3
"""A script to convert a dataset of YOLO annotations to a COCO dataset."""

import pathlib
import json
import shutil

import cv2
from PIL import Image


_SAVE_DIR = pathlib.Path("./src/train/data/tire-dataset")
_IMG_SAVE_DIR = _SAVE_DIR / "images"
_IMG_SAVE_DIR.mkdir(parents=True, exist_ok=True)
_IMG_DIR = pathlib.Path("./src/train/data/images")
_LABELS_DIR = pathlib.Path("./src/train/data/labels")
_IMG_EXTS = [".jpg", ".jpeg", ".png"]


coco_dataset = {
    "categories": [{"name": "tire", "id": 0}],
    "images": [],
    "annotations": [],
}
images = []
for ext in _IMG_EXTS:
    images += list(_IMG_DIR.glob(f"*{ext}"))

for idx, img in enumerate(images):

    label_path = _LABELS_DIR / img.with_suffix(".txt").name

    if not label_path.is_file():
        continue
    coco_dataset["images"].append({"file_name": img.name, "id": idx})

    img_width, img_height = Image.open(img).size
    label_data = []
    image = cv2.imread(str(img))
    for line in label_path.read_text().splitlines():
        class_id, x, y, w, h = line.split()
        class_id, x, y, w, h = int(class_id), float(x), float(y), float(w), float(h)

        if class_id == 0:
            b = [x * img_width, y * img_height, w * img_width, h * img_height]
            b[0] -= 0.5 * b[2]
            b[1] -= 0.5 * b[3]
            if b[2] > 0 and b[3] > 0:
                coco_dataset["annotations"].append(
                    {
                        "id": len(coco_dataset["annotations"]),
                        "bbox": b,
                        "category_id": class_id,
                        "image_id": idx,
                    }
                )

                cv2.rectangle(
                    image,
                    (int(b[0]), int(b[1])),
                    (int(b[0] + b[2]), int(b[1] + b[3])),
                    (0, 255, 0),
                    2,
                )

    shutil.copy2(img, _IMG_SAVE_DIR / img.name)

    cv2.imwrite(f"./src/train/data/drawn/{img.name}", image)

save_path = _SAVE_DIR / "annotations.json"
save_path.write_text(json.dumps(coco_dataset, indent=2))
