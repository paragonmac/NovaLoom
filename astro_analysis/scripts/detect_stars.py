#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detect stars in the image section.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH
from data_processing.fits_loader import load_fits_file
from data_processing.star_detection import estimate_background, detect_sources

def run_star_detection(data: np.ndarray, fwhm: float = 3.0, threshold_factor: float = 5.0):
    """
    Run star detection on the image data.
    
    Parameters
    ----------
    data : np.ndarray
        The image data
    fwhm : float
        Expected star Full-Width Half-Max in pixels
    threshold_factor : float
        Factor to multiply by noise std to get the detection threshold
    """
    try:
        # Estimate background and get noise level
        print("\nEstimating background...")
        box_size = (50, 50)  # Adjust based on your image characteristics
        filter_size = (3, 3)  # Size of median filter for background smoothing
        data_subtracted, noise_std = estimate_background(data, box_size, filter_size)
        
        # Calculate detection threshold
        threshold = threshold_factor * noise_std
        print(f"\nDetection Parameters:")
        print(f"FWHM: {fwhm}")
        print(f"Noise std: {noise_std:.2f}")
        print(f"Threshold: {threshold:.2f} ({threshold_factor} * {noise_std:.2f})")
        
        # Detect sources
        print("\nDetecting sources...")
        sources = detect_sources(data_subtracted, fwhm, threshold)
        
        # Format the output
        for col in sources.colnames:
            if col not in ('id', 'npix'):
                sources[col].info.format = '%.2f'
        
        # Print the results
        print(f"\nFound {len(sources)} sources:")
        sources.pprint(max_width=76)
        
        # Convert to DataFrame and save to CSV
        sources_df = sources.to_pandas()
        csv_path = "detected_stars.csv"
        sources_df.to_csv(csv_path, index=False)
        print(f"\nSaved sources to {csv_path}")
        
        return sources, sources_df
        
    except Exception as e:
        print(f"Error during star detection: {e}")
        return None, None

if __name__ == "__main__":
    try:
        # Load the FITS file
        data, header, wcs = load_fits_file(FITS_FILE_PATH)
        
        # Run star detection
        sources, sources_df = run_star_detection(data)
        
    except Exception as e:
        print(f"Error: {e}") 