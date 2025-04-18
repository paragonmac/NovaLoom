import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from typing import Tuple, Optional, Union, Any

def load_fits_file(fits_file_path: str) -> Tuple[np.ndarray, fits.header.Header, WCS]:
    """
    Load and process a FITS file.
    
    Parameters
    ----------
    fits_file_path : str
        Path to the FITS file
        
    Returns
    -------
    Tuple[np.ndarray, fits.header.Header, WCS]
        A tuple containing:
        - data: The processed image data as a numpy array
        - header: The FITS header
        - wcs: The WCS object for coordinate transformation
        
    Raises
    ------
    FileNotFoundError
        If the FITS file cannot be found
    ValueError
        If no valid image HDU is found or if the data is not 2-dimensional
    Exception
        For other errors during file loading or processing
    """
    try:
        with fits.open(fits_file_path) as hdul:
            # Find the first HDU with valid image data
            hdu_index = -1
            for i, hdu_item in enumerate(hdul):
                if hdu_item.data is not None and hdu_item.is_image and hdu_item.data.ndim >= 2:
                    hdu_index = i
                    break
                    
            if hdu_index == -1:
                raise ValueError("Could not find a valid image HDU in the FITS file.")

            hdu = hdul[hdu_index]
            header = hdu.header
            data = np.array(hdu.data, dtype=np.float64)

            # Handle multi-dimensional data
            if data.ndim > 2:
                if data.shape[0] == 1:
                    data = data.squeeze(axis=0)
                else:
                    data = data[0]

            if data.ndim != 2:
                raise ValueError(f"Data must be 2-dimensional for analysis, but got shape {data.shape}")

            wcs = WCS(header)
            if not wcs.is_celestial:
                raise ValueError("FITS header does not contain valid celestial WCS information.")

            return data, header, wcs

    except FileNotFoundError:
        raise FileNotFoundError(f"FITS file not found at '{fits_file_path}'")
    except Exception as e:
        raise Exception(f"Error loading FITS file: {e}") 