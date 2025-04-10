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
    from astro_analysis.scripts.load_fits import load_fits_file
    print("\nSuccessfully imported load_fits")
except Exception as e:
    print(f"Error importing load_fits: {e}")

try:
    from astro_analysis.scripts.display_section import display_section
    print("Successfully imported display_section")
except Exception as e:
    print(f"Error importing display_section: {e}")

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