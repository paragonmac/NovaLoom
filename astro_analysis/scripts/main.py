#!/usr/bin/env python
"""Unified CLI pipeline: load FITS, detect sources, visualize results.

This version uses the shared Lua settings (config/settings.lua) via SettingsManager.
Command-line overrides (fits path, fwhm, threshold factor) are supported and can
optionally persist back into the settings file unless --no-save is passed.
"""
from __future__ import annotations
import logging
import numpy as np
import matplotlib.pyplot as plt
from ._cli_common import build_arg_parser, init_logging, load_settings, get_fits
from astro_analysis.data_processing.star_detection import estimate_background, detect_sources  # type: ignore
from astro_analysis.visualization.plotting import plot_image_with_labels  # type: ignore

def display_fits_info(data, header, wcs):
    """Display FITS file information."""
    log = logging.getLogger("pipeline.fits")
    log.info("Displaying FITS file information")
    print("\nImage Data Shape:", data.shape)
    print("\nImage Data Type:", data.dtype)
    print("\nImage Data Range:", np.nanmin(data), "to", np.nanmax(data))
    
    print("\nFITS Header:")
    for key in header.keys():
        if key not in ['COMMENT', 'HISTORY']:
            print(f"{key}: {header[key]}")
    
    print("\nWCS Information:")
    print(wcs)
    
    # Display a small section of the data
    print("\nSample of Image Data (first 5x5 pixels):")
    print(data[0:5, 0:5])

def run_star_detection(data, fwhm=3.0, threshold_factor=5.0):
    """Run star detection on the image data."""
    log = logging.getLogger("pipeline.detect")
    try:
        # Estimate background and get noise level
        log.info("Estimating background and detecting stars")
        box_size = (50, 50)
        filter_size = (3, 3)
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
    log.info(f"Saved detected stars to {csv_path}")
        
        return sources, sources_df
        
    except Exception as e:
        log.error(f"Error during star detection: {e}")
        return None, None

def visualize_results(data, sources_df, wcs, header, fits_path: str | None):
    """Create visualization of detected stars."""
    log = logging.getLogger("pipeline.visualize")
    try:
        log.info("Creating visualization of detected stars")
        log.warning("Star information (magnitude, classification) not yet added to labels")
        
        fig = plot_image_with_labels(
            data=data,
            sources_df=sources_df,
            wcs=wcs,
            header=header,
            fits_file_path=fits_path or ''
        )
        
        # Save the figure
        output_path = "annotated_stars.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    log.info(f"Saved visualization to {output_path}")
        
        # Display the plot
        plt.show()
        
    except Exception as e:
        log.error(f"Error during visualization: {e}")

def main():
    parser = build_arg_parser("Run full analysis pipeline: load, detect, visualize")
    args = parser.parse_args()
    init_logging(args.debug)
    log = logging.getLogger("pipeline")
    sm = load_settings(args)
    try:
        data, header, wcs = get_fits(sm.settings)
    except Exception as e:
        log.error(f"Failed to load FITS: {e}")
        return 1
    log.info("Loaded FITS file")
    display_fits_info(data, header, wcs)

    fwhm = sm.settings['analysis']['star_detection']['fwhm']
    thresh_factor = sm.settings['analysis']['star_detection']['threshold_factor']
    sources, sources_df = run_star_detection(data, fwhm=fwhm, threshold_factor=thresh_factor)
    if sources_df is not None:
        log.info("Visualization step starting")
        visualize_results(data, sources_df, wcs, header, sm.settings.get('fits_file_path'))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys as _sys
    _sys.exit(main())