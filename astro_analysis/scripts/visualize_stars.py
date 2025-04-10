#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visualize detected stars in the FITS image.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH
from data_processing.fits_loader import load_fits_file
from visualization.plotting import plot_image_with_labels

def visualize_stars():
    """Load data and create visualization of detected stars."""
    try:
        # Load the FITS file
        print(f"Loading FITS file: {FITS_FILE_PATH}")
        data, header, wcs = load_fits_file(FITS_FILE_PATH)
        
        # Load detected stars from CSV
        csv_path = "detected_stars.csv"
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found. Please run detect_stars.py first.")
            return
            
        print(f"Loading detected stars from {csv_path}")
        sources_df = pd.read_csv(csv_path)
        
        # Create the visualization
        print("\nCreating visualization...")
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
        print(f"\nSaved visualization to {output_path}")
        
        # Display the plot
        plt.show()
        
    except Exception as e:
        print(f"Error during visualization: {e}")

if __name__ == "__main__":
    visualize_stars() 