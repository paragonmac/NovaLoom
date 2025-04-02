# NovaLoom

A Python toolkit tailored for students and academics to explore astronomical data through visualization, astrometric analysis, and modeling. Built with Astropy and supporting libraries, NovaLoom aims to serve as a collaborative resource emphasizing education, interactive learning, and analysis of celestial phenomena.

This repository currently focuses on processing astronomical FITS images, including source detection and cross-identification with known objects using Simbad.

## Features (identify_stars_in_fits.py)

*   Loads astronomical FITS images.
*   Parses World Coordinate System (WCS) information from FITS headers.
*   Performs background estimation and subtraction.
*   Detects star-like sources using `photutils.DAOStarFinder`.
*   Converts detected source pixel coordinates to RA/Dec using WCS.
*   Queries the Simbad database online to identify known objects near detected sources.
*   Visualizes the FITS image using Matplotlib.
*   Overlays labels with Simbad names directly onto the image plot for identified sources.
*   Prints a table of identified sources with their coordinates and Simbad details.

## Files Included

*   **identify_stars_in_fits.py** (or your chosen script name)
    *   A comprehensive Python script that performs the full workflow: loading FITS, finding sources, querying Simbad, and plotting results with labels.
*   **fits_files.ipynb**
    *   A Jupyter notebook potentially demonstrating earlier steps or alternative analyses for loading, analyzing, and visualizing FITS image files.

## Setup & Installation (Windows Recommended)

1.  **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/windows/). **Important:** Ensure you check the box "Add Python X.X to PATH" during installation.

2.  **Install Dependencies**: Open Command Prompt (cmd) or PowerShell and run the following command:

    ```cmd
    pip install numpy pandas matplotlib astropy photutils astroquery
    ```

## Usage

### identify_stars_in_fits.py

1.  **Configure the Script**: Open the `identify_stars_in_fits.py` file in a text editor or IDE. Modify the parameters in the **`--- Configuration ---`** section near the top:
    *   **`fits_file_path`**: **Crucially, set this** to the full path of your input FITS file (e.g., `'C:\\Users\\YourName\\Documents\\AstroData\\M42_image.fits'`).
    *   `source_fwhm_estimate`: Estimate the Full-Width Half-Maximum (size) of typical stars in your image, in pixels. This is vital for good source detection.
    *   `detection_sigma`: Set the detection threshold (how many standard deviations above the background noise a source must be). Lower values find more (potentially faint or noisy) sources.
    *   `simbad_search_radius`: Adjust the search radius (in arcseconds) for Simbad queries.
    *   _(Optionally adjust other parameters like `min_flux_for_labeling`, plotting colors/fonts, etc.)_

2.  **Run the Script**: Navigate to the directory containing the script in your Command Prompt or PowerShell and execute:

    ```cmd
    python identify_stars_in_fits.py
    ```

3.  **Output**: The script will print progress information to the console, display a plot of your FITS image with identified star names overlaid, and finally print a table of the identified sources to the console.

### fits_files.ipynb (Optional)

1.  **Launch Jupyter Notebook**: Open Command Prompt or PowerShell, navigate to the repository directory, and run:

    ```cmd
    jupyter notebook fits_files.ipynb
    ```
    This will open the notebook in your web browser.

2.  **Run Cells**: Execute the code cells within the notebook sequentially to see their individual outputs.

## Dependencies

*   [numpy](https://numpy.org/)
*   [pandas](https://pandas.pydata.org/)
*   [matplotlib](https://matplotlib.org/)
*   [astropy](https://www.astropy.org/)
*   [photutils](https://photutils.readthedocs.io/)
*   [astroquery](https://astroquery.readthedocs.io/)

## Notes

*   Ensure all file paths used within the scripts are correct for your system. Use full paths if necessary.
*   The accuracy of Simbad identifications heavily depends on the accuracy of the World Coordinate System (WCS) information in your FITS file header. If no sources are identified, consider checking or improving your image's WCS solution (plate-solving).
*   Simbad queries require an active internet connection.

## License

This project is licensed under the MIT License. See the LICENSE file for details.