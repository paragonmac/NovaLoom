import numpy as np
from astropy.stats import SigmaClip, mad_std
from photutils.detection import DAOStarFinder
from photutils.background import Background2D, MedianBackground

def estimate_background(data, box_size, filter_size):
    """
    Estimate the background of the image.
    
    Parameters:
    -----------
    data : numpy.ndarray
        The image data
    box_size : tuple
        Size of boxes for background estimation
    filter_size : tuple
        Size of median filter for background smoothing
        
    Returns:
    --------
    tuple
        (background_subtracted_data, noise_std)
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

def detect_sources(data, fwhm, threshold):
    """
    Detect sources in the image using DAOStarFinder.
    
    Parameters:
    -----------
    data : numpy.ndarray
        The image data (background subtracted)
    fwhm : float
        Expected star Full-Width Half-Max in pixels
    threshold : float
        Detection threshold above background noise
        
    Returns:
    --------
    astropy.table.Table
        Table of detected sources
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