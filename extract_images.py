"""
Extract every chart image from the notebook into individual PNG files,
ready to upload to GitHub.

Usage:
    1. Make sure you've already run the whole notebook (Kernel -> Restart & Run All)
       so the charts exist inside the .ipynb file.
    2. Run this script from the same folder as your notebook:
           python extract_images.py
    3. Look inside the new "images" folder for your PNG files.
"""

import nbformat
import base64
import os

NOTEBOOK_FILE = "analisis_guiado.ipynb"
OUTPUT_FOLDER = "images"

nb = nbformat.read(NOTEBOOK_FILE, as_version=4)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    for output in cell.get("outputs", []):
        data = output.get("data", {})
        if "image/png" in data:
            count += 1
            image_bytes = base64.b64decode(data["image/png"])
            filename = os.path.join(OUTPUT_FOLDER, f"chart_{count:02d}.png")
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {filename}")

print(f"\nDone. Extracted {count} images into the '{OUTPUT_FOLDER}' folder.")
