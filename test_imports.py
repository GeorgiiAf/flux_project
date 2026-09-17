"""Test if all required packages are installed."""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

packages = [
    'numpy',
    'pandas', 
    'cv2',
    'torch',
    'ultralytics',
    'easyocr',
    'matplotlib',
    'seaborn'
]

print("Testing package imports:")
print("-" * 50)

for package in packages:
    try:
        __import__(package)
        print(f"✓ {package:20} - OK")
    except ImportError as e:
        print(f"✗ {package:20} - MISSING")
        print(f"  Error: {e}")

print("-" * 50)
print("\nIf any packages are missing, install with:")
print("python -m pip install <package-name>")
