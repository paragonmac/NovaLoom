#!/usr/bin/env python
"""CLI: Detect stars using current settings (Lua) with optional overrides.

Examples:
    python -m astro_analysis.scripts.detect_stars
    python -m astro_analysis.scripts.detect_stars --fits Data/file.fit --fwhm 4 --threshold-factor 6
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from ._cli_common import build_arg_parser, init_logging, load_settings, get_fits
from astro_analysis.data_processing.star_detection import estimate_background, detect_sources  # type: ignore

def run_star_detection(data: np.ndarray, fwhm: float = 3.0, threshold_factor: float = 5.0):
    """
    Run star detection on the image data.
    
    Parameters
    ----------
    data : np.ndarray
        The image data
    fwhm : float
        Expected star Full-Width Half-Max in pixels
    threshold_factor : float
        Factor to multiply by noise std to get the detection threshold
    """
    try:
        # Estimate background and get noise level
        print("\nEstimating background...")
        box_size = (50, 50)  # Adjust based on your image characteristics
        filter_size = (3, 3)  # Size of median filter for background smoothing
        data_subtracted, noise_std = estimate_background(data, box_size, filter_size)
        
        # Calculate detection threshold
        threshold = threshold_factor * noise_std
        print(f"\nDetection Parameters:")
        print(f"FWHM: {fwhm}")
        print(f"Noise std: {noise_std:.2f}")
        print(f"Threshold: {threshold:.2f} ({threshold_factor} * {noise_std:.2f})")
        
        # Detect sources
        print("\nDetecting sources...")
        sources = detect_sources(data_subtracted, fwhm, threshold)
        
        # Format the output
        for col in sources.colnames:
            if col not in ('id', 'npix'):
                sources[col].info.format = '%.2f'
        
        # Print the results
        print(f"\nFound {len(sources)} sources:")
        sources.pprint(max_width=76)
        
        # Convert to DataFrame and save to CSV
        sources_df = sources.to_pandas()
        csv_path = "detected_stars.csv"
        sources_df.to_csv(csv_path, index=False)
        print(f"\nSaved sources to {csv_path}")
        
        return sources, sources_df
        
    except Exception as e:
        print(f"Error during star detection: {e}")
        return None, None

def main():
    parser = build_arg_parser("Detect stars in a FITS image")
    args = parser.parse_args()
    init_logging(args.debug)
    sm = load_settings(args)
    try:
        data, header, wcs = get_fits(sm.settings)
    except Exception as e:
        print(f"Error loading FITS: {e}")
        return 1
    fwhm = sm.settings['analysis']['star_detection']['fwhm']
    thresh_factor = sm.settings['analysis']['star_detection']['threshold_factor']
    run_star_detection(data, fwhm=fwhm, threshold_factor=thresh_factor)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys as _sys
    _sys.exit(main())