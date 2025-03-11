# NovaLoom
 A Python toolkit tailored for students and academics to explore astronomical data through visualization, astrometric analysis, and modeling. Built with Astropy and supporting libraries, AstroNexus serves as a collaborative resource emphasizing education, interactive learning, and future-oriented modeling of celestial phenomena.


# Astro Image Processing for Windows

This repository contains Python scripts and Jupyter notebooks specifically tailored for processing and visualizing astronomical FITS files on Windows systems.

## Files Included

- **Astro.py**  
  Python script for loading, analyzing, and visualizing astronomical FITS image data using Astropy and Matplotlib.

- **fits_files.ipynb**  
  A Jupyter notebook demonstrating the loading, analysis, visualization, and star detection within FITS image files.

## Setup & Installation (Windows)

1. **Install Python**: [Download Python](https://www.python.org/downloads/windows/) and ensure it is added to PATH during installation.

2. **Install Dependencies**: Open Command Prompt and execute:

```cmd
pip install astropy matplotlib photutils
```

## Usage

### Astro.py

1. **Update the File Path**: Modify the path to your FITS file:

```python
hdul = fits.open('C:\\Path\\To\\Your\\File.fit')
```

2. **Run the Script**: Execute in Command Prompt:

```cmd
python Astro.py
```

### fits_files.ipynb

1. Launch Jupyter Notebook:

```cmd
jupyter notebook fits_files.ipynb
```

2. Run each cell sequentially to process and visualize FITS images.

## Dependencies
- astropy
- matplotlib
- photutils

## Notes

- Ensure FITS file paths are accurate.
- Adjust paths within scripts to your local directories.

## License

This project is licensed under the MIT License.

