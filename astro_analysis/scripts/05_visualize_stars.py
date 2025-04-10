#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visualize the detected stars on the image.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from photutils.aperture import CircularAperture

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH

def visualize_stars(section, sources, aperture_radius=7.0, cmap='Greys', save_path=None):
    """
    Visualize the detected stars on the image.
    
    Parameters:
    -----------
    section : numpy.ndarray
        The image section
    sources : astropy.table.Table
        Table of detected sources
    aperture_radius : float
        Radius of the circular apertures in pixels
    cmap : str
        Colormap for the image
    save_path : str, optional
        Path to save the figure
    """
    # Create the figure
    plt.figure(figsize=(10, 8))
    
    # Display the image
    plt.imshow(section, cmap=cmap, origin='lower', norm=LogNorm(), interpolation='nearest')
    plt.colorbar(label='Intensity')
    plt.title('Detected Stars')
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    
    # Create circular apertures for each source
    positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
    apertures = CircularAperture(positions, r=aperture_radius)
    
    # Plot the apertures
    apertures.plot(color='blue', lw=1.5, alpha=0.5)
    
    # Save the figure if requested
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Figure saved to {save_path}")
    
    # Show the figure
    plt.show()

if __name__ == "__main__":
    # Import the functions from the previous scripts
    from astro_analysis.scripts.01_load_fits import load_fits_file
    from astro_analysis.scripts.02_display_section import display_section
    from astro_analysis.scripts.03_calculate_stats import calculate_stats
    from astro_analysis.scripts.04_detect_stars import detect_stars
    
    # Load the FITS file
    fits_file, image_data = load_fits_file()
    
    if image_data is not None:
        # Display a section of the image
        section = display_section(image_data)
        
        # Calculate statistics on the section
        mean, median, std = calculate_stats(section)
        
        # Detect stars in the section
        sources, sources_df = detect_stars(section, median, std=std)
        
        if sources is not None:
            # Visualize the detected stars
            visualize_stars(section, sources, save_path="annotated_stars.png")
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 