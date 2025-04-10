"""
Astro Analysis - A toolkit for astronomical image analysis

This package provides tools for:
- Loading and processing FITS files
- Detecting and analyzing stars
- Querying Simbad for star identification
- Creating visualizations of astronomical data
"""

__version__ = "0.1.0"

# Import commonly used functions to make them available at package level
from astro_analysis.data_processing.fits_loader import load_fits_file
from astro_analysis.data_processing.star_detection import estimate_background, detect_sources
from astro_analysis.data_processing.simbad_query import query_simbad
from astro_analysis.visualization.plotting import plot_image_with_labels

# Define what gets imported with 'from astro_analysis import *'
__all__ = [
    'load_fits_file',
    'estimate_background',
    'detect_sources',
    'query_simbad',
    'plot_image_with_labels'
] 