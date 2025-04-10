#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D visualization of the image.
"""

# Standard library imports
import os
import sys

# Third-party imports
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Add the parent directory to the path so we can import from astro_analysis
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the required functions directly from the script files
sys.path.append(os.path.dirname(__file__))
from config.settings import FITS_FILE_PATH

# Import functions from local script files
def import_function(script_name, function_name):
    """Import a function from a local script file."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        script_name, 
        os.path.join(os.path.dirname(__file__), script_name)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)

# Import the required functions
load_fits_file = import_function("01_load_fits.py", "load_fits_file")
display_section = import_function("02_display_section.py", "display_section")

def plot_3d_surface(section, cmap='viridis', save_path=None):
    """
    Create a 3D surface plot of the image.
    
    Parameters:
    -----------
    section : numpy.ndarray
        The image section
    cmap : str
        Colormap for the surface
    save_path : str, optional
        Path to save the figure
    """
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
    # Load the FITS file
    fits_file, image_data = load_fits_file()
    
    if image_data is not None:
        # Display a section of the image
        section = display_section(image_data)
        
        # Create a 3D surface plot
        plot_3d_surface(section, save_path="3d_surface.png")
        
        # Close the FITS file when done
        fits_file.close()
        print("\nFITS file closed.") 