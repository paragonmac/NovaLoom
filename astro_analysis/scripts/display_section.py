#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Display a section of the FITS image.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Add the parent directory to the path so we can import from astro_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FITS_FILE_PATH

def display_section(image_data, x_start=1500, x_end=2500, y_start=2500, y_end=3500, 
                   cmap='Greys', save_path=None):
    """
    Display a section of the FITS image.
    
    Parameters:
    -----------
    image_data : numpy.ndarray
        The image data
    x_start, x_end : int
        X-axis range for the section
    y_start, y_end : int
        Y-axis range for the section
    cmap : str
        Colormap for the image
    save_path : str, optional
        Path to save the figure
    """
    # Extract the section
    section = image_data[y_start:y_end, x_start:x_end]
    
    # Create the figure
    plt.figure(figsize=(10, 8))
    plt.imshow(section, origin='lower', norm=LogNorm(), cmap=cmap)
    plt.colorbar(label='Intensity')
    plt.title(f'FITS Image Section ({x_start}:{x_end}, {y_start}:{y_end})')
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    
    # Save the figure if requested
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Figure saved to {save_path}")
    
    # Show the figure
    plt.show()
    
    return section

if __name__ == "__main__":
    # Import the load_fits_file function from the previous script
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from astro_analysis.scripts.01_load_fits import load_fits_file
    
    # Load the FITS file
    fits_file, image_data = load_fits_file()
    
    if image_data is not None:
        # Display a section of the image
        section = display_section(image_data, save_path="image_section.png")
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 