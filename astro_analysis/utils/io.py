from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
from typing import Tuple

def read_fits(file_path: str) -> Tuple[np.ndarray, fits.Header, WCS]:
    """
    Read a FITS file and return the data, header, and WCS object.
    
    Parameters
    ----------
    file_path : str
        Path to the FITS file
        
    Returns
    -------
    Tuple[np.ndarray, fits.Header, WCS]
        The image data, FITS header, and WCS object
    """
    with fits.open(file_path) as hdul:
        # Get the primary HDU (first extension)
        hdu = hdul[0]
        
        # Get the data
        data = hdu.data
        
        # Get the header
        header = hdu.header
        
        # Create WCS object from header
        wcs = WCS(header)
        
        return data, header, wcs 