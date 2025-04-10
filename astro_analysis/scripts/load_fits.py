#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Load and display FITS file information.
"""

import os
import sys
import numpy as np

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH
from data_processing.fits_loader import load_fits_file

def display_fits_info():
    """Load a FITS file and display its structure."""
    print(f"Loading FITS file: {FITS_FILE_PATH}")
    
    try:
        data, header, wcs = load_fits_file(FITS_FILE_PATH)
        
        print("\nImage Data Shape:", data.shape)
        print("\nImage Data Type:", data.dtype)
        print("\nImage Data Range:", np.nanmin(data), "to", np.nanmax(data))
        
        print("\nFITS Header:")
        for key in header.keys():
            if key not in ['COMMENT', 'HISTORY']:
                print(f"{key}: {header[key]}")
        
        print("\nWCS Information:")
        print(wcs)
        
        # Display a small section of the data
        print("\nSample of Image Data (first 5x5 pixels):")
        print(data[0:5, 0:5])
        
    except FileNotFoundError:
        print(f"Error: FITS file not found at {FITS_FILE_PATH}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error loading FITS file: {e}")

if __name__ == "__main__":
    display_fits_info() 