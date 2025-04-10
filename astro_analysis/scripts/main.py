import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord

from astro_analysis.config.settings import (
    FITS_FILE_PATH, IGNORE_WARNINGS, BACKGROUND_BOX_SIZE,
    BACKGROUND_FILTER_SIZE, DETECTION_SIGMA, SOURCE_FWHM_ESTIMATE,
    SIMBAD_SEARCH_RADIUS, SIMBAD_TIMEOUT, MIN_FLUX_FOR_LABELING,
    PLOT_LABEL_FONTSIZE, PLOT_LABEL_COLOR, PLOT_CMAP
)
from astro_analysis.data_processing.fits_loader import load_fits_file
from astro_analysis.data_processing.star_detection import estimate_background, detect_sources
from astro_analysis.data_processing.simbad_query import query_simbad
from astro_analysis.utils.warnings import configure_warnings
from astro_analysis.visualization.plotting import plot_image_with_labels


def main() -> None:
    """Run the main analysis pipeline."""
    # Configure warnings
    if IGNORE_WARNINGS:
        configure_warnings()
        
    print(f"--- Processing FITS File: {FITS_FILE_PATH} ---")
    
    # Load FITS file
    print("\nStep 1: Loading FITS file and WCS...")
    data, header, wcs = load_fits_file(FITS_FILE_PATH)
    print(f"  Using HDU (Object: {header.get('OBJECT', 'Unknown')})")
    print(f"  Initial data shape: {data.shape}")
    print("  WCS loaded successfully.")
    
    # Estimate background and detect sources
    print("\nStep 2: Estimating background and finding sources...")
    data_subtracted, noise_std = estimate_background(
        data, BACKGROUND_BOX_SIZE, BACKGROUND_FILTER_SIZE
    )
    
    detection_threshold = DETECTION_SIGMA * noise_std
    print(f"  Using detection threshold: {detection_threshold:.2f}")
    
    sources = detect_sources(
        data_subtracted, SOURCE_FWHM_ESTIMATE, detection_threshold
    )
    print(f"  Found {len(sources)} sources.")
    
    # Convert pixel coordinates to RA/Dec
    print("\nStep 3: Converting pixel coordinates to RA/Dec...")
    pixel_coords_x = sources['xcentroid']
    pixel_coords_y = sources['ycentroid']
    world_coords = wcs.pixel_to_world(pixel_coords_x, pixel_coords_y)
    print(f"  Converted {len(world_coords)} coordinates.")
    
    # Add RA/Dec to sources table
    sources['ra'] = world_coords.ra.deg
    sources['dec'] = world_coords.dec.deg
    
    # Convert to DataFrame
    sources_df = sources.to_pandas()
    
    # Query Simbad
    print(f"\nStep 4: Querying Simbad for names...")
    sources_df = query_simbad(
        world_coords, sources_df, SIMBAD_SEARCH_RADIUS, 
        SIMBAD_TIMEOUT, MIN_FLUX_FOR_LABELING
    )
    
    # Create plot
    print("\nStep 5: Generating plot...")
    fig = plot_image_with_labels(
        data, sources_df, wcs, header, FITS_FILE_PATH,
        PLOT_LABEL_FONTSIZE, PLOT_LABEL_COLOR, PLOT_CMAP
    )
    plt.show()
    
    # Print identified sources
    print("\n--- Sources with Identified Simbad Names ---")
    identified_sources = sources_df[
        pd.notna(sources_df['simbad_name']) & 
        (sources_df['simbad_name'] != "Query Error")
    ]
    
    if not identified_sources.empty:
        cols_to_show = ['xcentroid', 'ycentroid', 'flux', 'ra', 'dec', 
                       'simbad_name', 'simbad_otype']
        cols_exist = [col for col in cols_to_show if col in identified_sources.columns]
        rounding = {'xcentroid':1, 'ycentroid':1, 'flux':1, 'ra':5, 'dec':5}
        rounding_applied = {k: v for k, v in rounding.items() 
                          if k in identified_sources.columns and 
                          pd.api.types.is_numeric_dtype(identified_sources[k])}
        
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 120)
        print(identified_sources[cols_exist].round(rounding_applied))
    else:
        print("No sources were successfully identified via Simbad.")
        
    print("\n--- Script Finished ---")

if __name__ == "__main__":
    main() 