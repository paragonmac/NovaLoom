#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calculate statistics on the image section.
"""

import os
import sys
import numpy as np
from astropy.stats import sigma_clipped_stats

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH

def calculate_stats(section, sigma=3.0):
    """
    Calculate statistics on the image section using sigma-clipping.
    
    Parameters:
    -----------
    section : numpy.ndarray
        The image section
    sigma : float
        Sigma value for sigma-clipping
        
    Returns:
    --------
    tuple
        (mean, median, std) - The calculated statistics
    """
    # Calculate statistics using sigma-clipping
    mean, median, std = sigma_clipped_stats(section, sigma=sigma)
    
    # Print the results
    print(f"\nStatistics (sigma={sigma}):")
    print(f"Mean: {mean:.2f}")
    print(f"Median: {median:.2f}")
    print(f"Standard Deviation: {std:.2f}")
    
    return mean, median, std

if __name__ == "__main__":
    # Import the functions from the previous scripts
    from astro_analysis.lib.load_fits import load_fits_file
    from astro_analysis.lib.display_section import display_section
    
    # Load the FITS file
    fits_file, image_data = load_fits_file()
    
    if image_data is not None:
        # Display a section of the image
        section = display_section(image_data)
        
        # Calculate statistics on the section
        mean, median, std = calculate_stats(section)
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 