#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main script for astronomical image analysis.
Combines functionality for loading FITS files, detecting stars, and visualizing results.

TODO:
- Add star information (magnitude, classification) to visualization labels
- Add support for multiple FITS files in batch processing
- Add command line arguments for configuration
- Add progress bars for long-running operations
- Add support for different output formats (PDF, SVG)
- Add unit tests for all functions
- Add logging configuration file
- Add support for different star detection algorithms
- Add support for custom WCS transformations
- Add support for different coordinate systems
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH
from data_processing.fits_loader import load_fits_file
from data_processing.star_detection import estimate_background, detect_sources
from visualization.plotting import plot_image_with_labels

def display_fits_info(data, header, wcs):
    """Display FITS file information."""
    logger.info("Displaying FITS file information")
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

def run_star_detection(data, fwhm=3.0, threshold_factor=5.0):
    """Run star detection on the image data."""
    try:
        # Estimate background and get noise level
        logger.info("Estimating background and detecting stars")
        box_size = (50, 50)
        filter_size = (3, 3)
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
        logger.info(f"Saved detected stars to {csv_path}")
        
        return sources, sources_df
        
    except Exception as e:
        logger.error(f"Error during star detection: {e}")
        return None, None

def visualize_results(data, sources_df, wcs, header):
    """Create visualization of detected stars."""
    try:
        logger.info("Creating visualization of detected stars")
        logger.warning("Star information (magnitude, classification) not yet added to labels")
        
        fig = plot_image_with_labels(
            data=data,
            sources_df=sources_df,
            wcs=wcs,
            header=header,
            fits_file_path=FITS_FILE_PATH
        )
        
        # Save the figure
        output_path = "annotated_stars.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved visualization to {output_path}")
        
        # Display the plot
        plt.show()
        
    except Exception as e:
        logger.error(f"Error during visualization: {e}")

def main():
    """Main function to run the complete analysis pipeline."""
    try:
        logger.info("Starting astronomical image analysis")
        # Load the FITS file
        print(f"Loading FITS file: {FITS_FILE_PATH}")
        data, header, wcs = load_fits_file(FITS_FILE_PATH)
        
        # Display FITS information
        display_fits_info(data, header, wcs)
        
        # Run star detection
        sources, sources_df = run_star_detection(data)
        
        if sources_df is not None:
            # Visualize results
            visualize_results(data, sources_df, wcs, header)
            
    except FileNotFoundError:
        logger.error(f"FITS file not found at {FITS_FILE_PATH}")
    except Exception as e:
        logger.error(f"Error in main pipeline: {e}")

if __name__ == "__main__":
    main() 