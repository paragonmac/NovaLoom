#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D visualization of astronomical image data.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.io import fits

def load_fits_file(file_path):
    """Load a FITS file and return its data."""
    try:
        fits_file = fits.open(file_path)
        image_data = fits_file[0].data
        return fits_file, image_data
    except Exception as e:
        print(f"Error loading FITS file: {e}")
        return None, None

def display_section(image_data, x_start=1500, x_end=2500, y_start=2500, y_end=3500):
    """Extract and return a section of the image."""
    try:
        section = image_data[x_start:x_end, y_start:y_end]
        return section
    except Exception as e:
        print(f"Error extracting section: {e}")
        return None

def plot_3d_surface(section, cmap='viridis', save_path=None):
    """
    Create a 3D surface plot of the image section.
    
    Parameters:
    -----------
    section : numpy.ndarray
        The image section to plot
    cmap : str
        Colormap for the surface
    save_path : str, optional
        Path to save the figure
    """
    if section is None:
        print("No valid data to plot")
        return
    
    # Create the figure
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create the grid
    X, Y = np.meshgrid(np.arange(section.shape[1]), np.arange(section.shape[0]))
    
    # Plot the surface
    surf = ax.plot_surface(X, Y, section, cmap=cmap, linewidth=0, antialiased=False)
    
    # Add labels and title
    ax.set_title('3D Surface of Star Intensities')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Intensity')
    
    # Add a color bar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    # Save the figure if requested
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Figure saved to {save_path}")
    
    # Show the figure
    plt.show()

if __name__ == "__main__":
    # Set the path to the FITS file
    fits_file_path = 'Data/Light_M42_180.0s_Bin1_0016.fit'
    
    # Load the FITS file
    fits_file, image_data = load_fits_file(fits_file_path)
    
    if image_data is not None:
        # Extract a section of the image
        section = display_section(image_data)
        
        if section is not None:
            # Create a 3D surface plot
            plot_3d_surface(section, save_path="3d_surface.png")
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 