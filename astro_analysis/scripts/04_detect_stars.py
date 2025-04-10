#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detect stars in the image section.
"""

import os
import sys
import numpy as np
import pandas as pd
from photutils.detection import DAOStarFinder

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH

def detect_stars(section, median, fwhm=3.0, threshold_factor=5.0, std=None):
    """
    Detect stars in the image section using DAOStarFinder.
    
    Parameters:
    -----------
    section : numpy.ndarray
        The image section
    median : float
        Median value of the section (for background subtraction)
    fwhm : float
        Expected star Full-Width Half-Max in pixels
    threshold_factor : float
        Factor to multiply by std to get the detection threshold
    std : float, optional
        Standard deviation of the section (if None, will be calculated)
        
    Returns:
    --------
    astropy.table.Table
        Table of detected sources
    """
    # Calculate the detection threshold
    if std is None:
        from astropy.stats import sigma_clipped_stats
        _, _, std = sigma_clipped_stats(section, sigma=3.0)
    
    threshold = threshold_factor * std
    print(f"\nDetection Parameters:")
    print(f"FWHM: {fwhm}")
    print(f"Threshold: {threshold:.2f} ({threshold_factor} * {std:.2f})")
    
    # Create the star finder
    daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold)
    
    # Run the star finder on the background-subtracted image
    sources = daofind(section - median)
    
    # Check if sources were found
    if sources is None or len(sources) == 0:
        print("No sources found with the given parameters.")
        return None
    
    # Format the output
    for col in sources.colnames:
        if col not in ('id', 'npix'):
            sources[col].info.format = '%.2f'
    
    # Print the results
    print(f"\nFound {len(sources)} sources:")
    sources.pprint(max_width=76)
    
    # Convert to DataFrame for easier manipulation
    sources_df = sources.to_pandas()
    
    # Save to CSV
    csv_path = "detected_stars.csv"
    sources_df.to_csv(csv_path, index=False)
    print(f"\nSaved sources to {csv_path}")
    
    return sources, sources_df

if __name__ == "__main__":
    # Import the functions from the previous scripts
    from astro_analysis.scripts.01_load_fits import load_fits_file
    from astro_analysis.scripts.02_display_section import display_section
    from astro_analysis.scripts.03_calculate_stats import calculate_stats
    
    # Load the FITS file
    fits_file, image_data = load_fits_file()
    
    if image_data is not None:
        # Display a section of the image
        section = display_section(image_data)
        
        # Calculate statistics on the section
        mean, median, std = calculate_stats(section)
        
        # Detect stars in the section
        sources, sources_df = detect_stars(section, median, std=std)
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 