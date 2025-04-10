import numpy as np
from astropy.stats import SigmaClip, mad_std
from photutils.detection import DAOStarFinder
from photutils.background import Background2D, MedianBackground
from typing import Tuple, Optional, Union
from astropy.table import Table

def estimate_background(
    data: np.ndarray,
    box_size: Tuple[int, int],
    filter_size: Tuple[int, int]
) -> Tuple[np.ndarray, float]:
    """
    Estimate the background of the image.
    
    Parameters
    ----------
    data : np.ndarray
        The image data
    box_size : Tuple[int, int]
        Size of boxes for background estimation
    filter_size : Tuple[int, int]
        Size of median filter for background smoothing
        
    Returns
    -------
    Tuple[np.ndarray, float]
        A tuple containing:
        - background_subtracted_data: The data with background subtracted
        - noise_std: The standard deviation of the noise
    """
    try:
        sigma_clip_bg = SigmaClip(sigma=3.0)
        bkg_estimator = MedianBackground()
        
        # Ensure box size is not larger than image dimensions
        actual_box_size = (min(box_size[0], data.shape[0]), 
                          min(box_size[1], data.shape[1]))
        
        bkg = Background2D(data, actual_box_size, filter_size=filter_size,
                          sigma_clip=sigma_clip_bg, bkg_estimator=bkg_estimator,
                          exclude_percentile=10.0)
        
        data_subtracted = data - bkg.background
        
        # Calculate noise level
        valid_rms = bkg.background_rms[np.isfinite(bkg.background_rms)]
        if len(valid_rms) > 0:
            noise_std = np.nanmedian(valid_rms)
        else:
            noise_std = mad_std(data_subtracted[np.isfinite(data_subtracted)])
            
        return data_subtracted, noise_std
        
    except Exception as e:
        print(f"Warning: Background estimation failed ({e})")
        print("Proceeding with source detection on original data.")
        noise_std = mad_std(data[np.isfinite(data)])
        return data, noise_std

def detect_sources(
    data: np.ndarray,
    fwhm: float,
    threshold: float
) -> Table:
    """
    Detect sources in the image using DAOStarFinder.
    
    Parameters
    ----------
    data : np.ndarray
        The image data (background subtracted)
    fwhm : float
        Expected star Full-Width Half-Max in pixels
    threshold : float
        Detection threshold above background noise
        
    Returns
    -------
    Table
        Table of detected sources
        
    Raises
    ------
    ValueError
        If the threshold is not positive or if no sources are found
    Exception
        For other errors during source detection
    """
    try:
        if threshold <= 0:
            raise ValueError(f"Detection threshold ({threshold:.2f}) must be positive.")
            
        daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold)
        sources = daofind(data)
        
        if sources is None or len(sources) == 0:
            raise ValueError(f"No sources found with FWHM={fwhm} and threshold={threshold:.2f}")
            
        return sources
        
    except Exception as e:
        raise Exception(f"Error during source finding: {e}") 