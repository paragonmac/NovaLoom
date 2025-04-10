import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from astro_analysis.config.settings import FITS_FILE_PATH
    print("Successfully imported settings")
    print(f"FITS_FILE_PATH = {FITS_FILE_PATH}")
except Exception as e:
    print(f"Error importing settings: {e}")

try:
    from astro_analysis.data_processing.fits_loader import load_fits_file
    print("\nSuccessfully imported fits_loader")
except Exception as e:
    print(f"Error importing fits_loader: {e}")

try:
    from astro_analysis.visualization.plotting import plot_image_with_labels
    print("Successfully imported plotting")
except Exception as e:
    print(f"Error importing plotting: {e}")

print("\nCurrent directory structure:")
for root, dirs, files in os.walk("astro_analysis"):
    level = root.replace("astro_analysis", "").count(os.sep)
    indent = " " * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 4 * (level + 1)
    for f in files:
        print(f"{subindent}{f}")

print("\nPython path:")
for path in sys.path:
    print(path) 