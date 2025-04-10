# Astronomical Image Analysis

This project provides a comprehensive toolkit for analyzing astronomical FITS images, detecting stars, and identifying them using the Simbad database. Whether you're a researcher, student, or astronomy enthusiast, this software will help you process and analyze astronomical images with ease.

## 🌟 Features

- 📁 FITS file loading and processing
- 🔍 Background estimation and star detection
- 🗺️ Coordinate transformation (pixel to RA/Dec)
- 🔎 Simbad database querying for star identification
- 📊 Visualization with labeled sources
- 🎨 3D surface visualization of astronomical data
- ⚠️ Comprehensive error handling and logging
- 📈 Statistical analysis of detected sources

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git
- A text editor or IDE (VS Code recommended)
- Basic understanding of astronomical FITS files

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd astro_analysis
   ```

2. **Set up a virtual environment** (strongly recommended)
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux:
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the installation**
   ```bash
   python -m astro_analysis.utils.test_imports
   ```
   This will check if all dependencies are properly installed and accessible.

## 📋 Usage Guide

### 1. Preparing Your Data

1. Place your FITS file in the appropriate directory
   - Default location: `Data/Light_M42_180.0s_Bin1_0016.fit`
   - Supported formats: Standard FITS files with WCS information

2. Configure your settings in `config/settings.py`:
   ```python
   FITS_FILE_PATH = "path/to/your/fits/file.fit"
   SOURCE_DETECTION_THRESHOLD = 3.0  # Adjust based on your image
   SIMBAD_QUERY_RADIUS = 5.0  # Arcseconds
   ```

### 2. Running the Analysis

You can run the complete analysis pipeline using:
```bash
python -m astro_analysis.scripts.main
```

Or run individual components:

1. **Load and display FITS file**
   ```bash
   python -m astro_analysis.scripts.load_fits
   ```

2. **Display a section of the image**
   ```bash
   python -m astro_analysis.scripts.display_section
   ```

3. **Detect stars**
   ```bash
   python -m astro_analysis.scripts.detect_stars
   ```

4. **Visualize detected stars**
   ```bash
   python -m astro_analysis.scripts.visualize_stars
   ```

5. **Create 3D visualization**
   ```bash
   python -m astro_analysis.scripts.visualize_3d
   ```

### 3. Understanding the Output

- The analysis will generate several output files:
  - `detected_sources.csv`: List of detected sources with coordinates
  - `identified_sources.csv`: Sources matched with Simbad database
  - Various visualization plots (PNG format)

## 📁 Project Structure

```
astro_analysis/
├── config/
│   └── settings.py         # Configuration parameters
├── data_processing/
│   ├── fits_loader.py      # FITS file loading and processing
│   ├── star_detection.py   # Star detection algorithms
│   └── simbad_query.py     # Simbad database interaction
├── utils/
│   ├── warnings.py         # Warning configuration
│   └── test_imports.py     # Import testing utility
├── visualization/
│   └── plotting.py         # Plotting functions
└── scripts/
    ├── main.py            # Main analysis pipeline
    ├── load_fits.py       # FITS file loading script
    ├── display_section.py # Image section display
    ├── detect_stars.py    # Star detection script
    ├── visualize_stars.py # Star visualization
    └── visualize_3d.py    # 3D visualization
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running commands from the project root directory
   - Verify your virtual environment is activated
   - Run `python -m astro_analysis.utils.test_imports` to diagnose import issues

2. **FITS File Issues**
   - Verify your FITS file has valid WCS information
   - Check file permissions
   - Ensure the file path in settings.py is correct

3. **Simbad Query Issues**
   - Check your internet connection
   - Verify the query radius in settings.py
   - Ensure the coordinates are in the correct format

### Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Look for similar issues in the project's issue tracker
3. Create a new issue with:
   - Your Python version
   - Operating system
   - Complete error message
   - Steps to reproduce the issue

## 📚 Dependencies

- numpy: Numerical computations
- pandas: Data manipulation
- matplotlib: Basic plotting
- astropy: Astronomical data handling
- photutils: Source detection
- astroquery: Simbad database access
- seaborn: Statistical visualizations
- plotly: Interactive visualizations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your code:
- Follows PEP 8 style guidelines
- Includes docstrings and comments
- Has appropriate test coverage
- Updates documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows for:
- Commercial use
- Modification
- Distribution
- Private use

The only requirement is that the license and copyright notice must be included in all copies or substantial portions of the software.

## 🙏 Acknowledgments

- Astropy community for their excellent documentation
- Simbad database for providing star identification data
- All the genius that helped answer my questions

---

For more detailed information about specific features or advanced usage, please refer to the documentation in each module's docstrings or create an issue for specific questions.