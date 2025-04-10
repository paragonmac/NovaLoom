import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.visualization import ZScaleInterval

def plot_image_with_labels(data, sources_df, wcs, header, fits_file_path, 
                          label_fontsize=7, label_color='cyan', cmap='magma'):
    """
    Create a plot of the image with labeled sources.
    
    Parameters:
    -----------
    data : numpy.ndarray
        The image data
    sources_df : pandas.DataFrame
        DataFrame containing source information
    wcs : astropy.wcs.WCS
        WCS object for coordinate transformation
    header : astropy.io.fits.header.Header
        FITS header
    fits_file_path : str
        Path to the FITS file
    label_fontsize : int
        Font size for labels
    label_color : str
        Color for labels
    cmap : str
        Colormap for the image
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    fig = plt.figure(figsize=(15, 15))
    
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
        
    # Display image
    ax.imshow(data, cmap=cmap, origin='lower', vmin=vmin, vmax=vmax, 
              interpolation='nearest')
              
    # Add labels for sources
    labeled_count = 0
    for index, source in sources_df.iterrows():
        simbad_name = source['simbad_name']
        if pd.notna(simbad_name) and simbad_name != "Query Error":
            x_pos = source['xcentroid']
            y_pos = source['ycentroid']
            
            ax.text(x_pos + 5, y_pos + 5, simbad_name,
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
                f"{labeled_count} Sources Labeled (Simbad Identification)")
                
    plt.tight_layout()
    return fig 