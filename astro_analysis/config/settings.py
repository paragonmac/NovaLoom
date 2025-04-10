import astropy.units as u

# FITS file configuration
FITS_FILE_PATH = 'Data/Light_M42_180.0s_Bin1_0016.fit'

# Source Detection Parameters
SOURCE_FWHM_ESTIMATE = 5.0  # Estimated star Full-Width Half-Max in pixels
DETECTION_SIGMA = 5.0  # Sigma threshold above background noise for detection
BACKGROUND_BOX_SIZE = (50, 50)  # Size of boxes (pixels) for background estimation
BACKGROUND_FILTER_SIZE = (3, 3)  # Size of median filter (pixels) for background smoothing

# Simbad Query Parameters
SIMBAD_SEARCH_RADIUS = 10 * u.arcsec  # Search radius around each source coordinate
SIMBAD_TIMEOUT = 30  # Seconds before Simbad query times out

# Plotting Parameters
PLOT_LABEL_FONTSIZE = 7  # Font size for the star names on the plot
PLOT_LABEL_COLOR = 'cyan'  # Color for the star names
MIN_FLUX_FOR_LABELING = 0  # Only label sources brighter than this flux
PLOT_CMAP = 'magma'  # Colormap for the image
FIGURE_SIZE = (15, 15)  # Size of the output plot figure in inches

# Warning Configuration
IGNORE_WARNINGS = True  # Whether to ignore common warnings 