import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.visualization import ZScaleInterval
from astropy.wcs import WCS
from astropy.io.fits import Header
from typing import Optional, Union
from matplotlib.figure import Figure

def plot_image_with_labels(
    data: np.ndarray,
    sources_df: pd.DataFrame,
    wcs: WCS,
    header: Header,
    fits_file_path: str,
    label_fontsize: int = 7,
    label_color: str = 'cyan',
    cmap: str = 'magma',
    fig: Optional[Figure] = None
) -> Figure:
    """
    Create a plot of the image with labeled sources.
    
    Parameters
    ----------
    data : np.ndarray
        The image data
    sources_df : pd.DataFrame
        DataFrame containing source information
    wcs : WCS
        WCS object for coordinate transformation
    header : Header
        FITS header
    fits_file_path : str
        Path to the FITS file
    label_fontsize : int, optional
        Font size for labels, defaults to 7
    label_color : str, optional
        Color for labels, defaults to 'cyan'
    cmap : str, optional
        Colormap for the image, defaults to 'magma'
    fig : Figure, optional
        Existing Matplotlib Figure to draw on. If None, a new figure is created.
        
    Returns
    -------
    Figure
        The created figure
        
    Notes
    -----
    The function creates a plot with:
    - The image displayed using the specified colormap
    - Labels for sources that have valid Simbad names
    - Proper WCS coordinate display if available
    - Grid lines and axis labels
    """
    # Use provided figure or create a new one
    if fig is None:
        fig = plt.figure(figsize=(15, 15))
    else:
        fig.clear() # Clear the existing figure before adding new axes
    
    try:
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        wcs_enabled = True
    except Exception as e:
        print(f"Warning: Failed to create plot with WCS projection ({e})")
        ax = fig.add_subplot(1, 1, 1)
        wcs_enabled = False
        
    # Calculate image scaling
    interval = ZScaleInterval()
    finite_data = data[np.isfinite(data)]
    if finite_data.size > 0:
        vmin, vmax = interval.get_limits(finite_data)
    else:
        vmin, vmax = 0, 1
        
    print(f"Displaying image with colormap '{cmap}' (vmin={vmin:.2f}, vmax={vmax:.2f})")
        
    # Display image
    ax.imshow(data, cmap=cmap, origin='lower', vmin=vmin, vmax=vmax, 
              interpolation='nearest')
              
    # Add labels for sources
    labeled_count = 0
    for index, source in sources_df.iterrows():
        # Use source ID as label if Simbad name is not available
        label = f"Source {int(source['id'])}"
        if 'simbad_name' in source and pd.notna(source['simbad_name']) and source['simbad_name'] != "Query Error":
            label = source['simbad_name']
            
        x_pos = source['xcentroid']
        y_pos = source['ycentroid']
        
        ax.text(x_pos + 5, y_pos + 5, label,
               color=label_color, fontsize=label_fontsize,
               ha='left', va='bottom',
               bbox=dict(boxstyle='round,pad=0.1', fc='black', 
                        alpha=0.5, ec='none'))
        labeled_count += 1
            
    # Add axis labels
    if wcs_enabled:
        ax.set_xlabel("Right Ascension")
        ax.set_ylabel("Declination")
        ax.grid(color='white', ls=':', alpha=0.4)
    else:
        ax.set_xlabel("Pixel X Coordinate")
        ax.set_ylabel("Pixel Y Coordinate")
        ax.grid(color='grey', ls=':', alpha=0.4)
        
    # Add title
    object_name = header.get('OBJECT', 'Field')
    ax.set_title(f"{object_name} ({fits_file_path.split('/')[-1]})\n"
                f"{labeled_count} Sources Labeled")
                
    plt.tight_layout()
    return fig 