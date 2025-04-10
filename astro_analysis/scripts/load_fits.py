#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Load and display FITS file information.
"""

import os
import sys
import numpy as np
from astropy.io import fits

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH

def load_fits_file():
    """Load a FITS file and display its structure."""
    print(f"Loading FITS file: {FITS_FILE_PATH}")
    
    try:
        fits_file = fits.open(FITS_FILE_PATH)
        print("\nFITS File Structure:")
        print(fits_file)
        
        # Extract image data from the primary HDU
        image_data = fits_file[0].data
        
        print("\nImage Data Shape:", image_data.shape)
        print("\nImage Data Type:", image_data.dtype)
        print("\nImage Data Range:", np.nanmin(image_data), "to", np.nanmax(image_data))
        
        # Display a small section of the data
        print("\nSample of Image Data (first 5x5 pixels):")
        print(image_data[0:5, 0:5])
        
        return fits_file, image_data
        
    except FileNotFoundError:
        print(f"Error: FITS file not found at {FITS_FILE_PATH}")
        return None, None
    except Exception as e:
        print(f"Error loading FITS file: {e}")
        return None, None

if __name__ == "__main__":
    fits_file, image_data = load_fits_file()
    
    if fits_file is not None:
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 