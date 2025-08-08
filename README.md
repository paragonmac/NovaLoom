# NovaLoom – Astronomical Image Analysis & Visualization

NovaLoom provides a desktop (PySide6) GUI and a collection of modular scripts for loading, analyzing, and visualizing astronomical FITS images. It supports star detection, basic catalog querying, interactive zoom / selection, and configurable visualization parameters. A Lua‑backed settings system plus rotating log capture make it easy to tune and debug workflows.

## 🌟 Features

GUI (NovaLoom):
- 🖥️ Modern PySide6 interface (run with `python NovaLoom.py`)
- 🔄 Live settings dialog (theme, font size, detection & visualization params)
- 🧪 Star detection & cached results reuse
- 🔍 Interactive zoom (in/out, reset) & selection modes with performance metrics
- 🪪 Debug logging toggle (Options → Enable Debug Logging) with live log dock
- 🧾 Rotating log file at `logs/novaloom.log` (font manager spam suppressed)

Core / Pipeline:
- 📁 FITS file loading & caching
- 🔍 Background estimation and star detection
- 🗺️ (Planned) Coordinate transformation (pixel → RA/Dec)
- 🔎 (Optional) Simbad database querying for star identification
- 📊 2D visualization with configurable colormap/interpolation & source overlays
- 🎨 3D surface visualization of data
- 📈 Statistical summaries of detected sources
- ⚠️ Structured error handling & performance timing instrumentation

## 🎯 Project Goals

### Short-term Goals
- Add star information (magnitude, classification) to visualization labels
- Implement batch processing for multiple FITS files
- Add command-line interface for easier configuration
- Add progress bars for long-running operations
- Support additional output formats (PDF, SVG)
- Implement unit tests for all functions
- Add logging configuration file

### Medium-term Goals
- Support different star detection algorithms
- Implement custom WCS transformations
- Add support for different coordinate systems
- Create a web interface for easier access
- Add support for different telescope data formats
- Implement machine learning for star classification
- Add support for time-series analysis

### Long-term Goals
- Create a full-featured astronomical image processing suite
- Support for real-time telescope data processing
- Integration with major astronomical databases
- Advanced photometry and astrometry tools
- Support for different wavelength ranges
- Automated report generation
- Collaborative features for research teams

### Simulation Goals

#### Short-term Simulation Goals
- Implement basic N-body simulation in C++ using OpenGL
- Add support for different gravitational force models
- Create basic visualization of particle systems
- Implement simple collision detection
- Add basic performance metrics and profiling
- Support for different time integration methods
- Basic particle system configuration files

#### Medium-term Simulation Goals
- Port to Vulkan for better performance
- Implement GPU acceleration for force calculations
- Add support for different particle types (stars, planets, etc.)
- Create interactive visualization controls
- Implement adaptive time stepping
- Add support for different boundary conditions
- Create simulation data export formats
- Add basic analysis tools for simulation results

#### Long-term Simulation Goals
- Create a full-featured N-body simulation engine
- Support for hierarchical time stepping
- Implement advanced collision handling
- Add support for different physical processes (gas dynamics, radiation, etc.)
- Create a web-based visualization interface
- Support for distributed computing
- Integration with astronomical databases
- Advanced analysis and visualization tools
- Support for different coordinate systems
- Create a plugin system for custom physics

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
   cd NovaLoom
   ```

2. **Set up a virtual environment** (strongly recommended)
   ```bash
   # On Windows:
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux:
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the installation (optional)**
   ```bash
   python -m astro_analysis.utils.test_imports
   ```
   This checks that the core analysis modules import correctly.

5. **Launch the GUI**
   ```bash
   python NovaLoom.py
   ```
   The main window will open. Use the toolbar or buttons to load a FITS file, analyze, and visualize results.

## 📋 Usage Guide

### Quick Start (GUI)
1. Place FITS files under `Data/` (or subfolders). A sample file is included.
2. Launch: `python NovaLoom.py`.
3. Load a FITS file (Load FITS button). If prior analysis exists, cached results are reused.
4. Click Analyze to run star detection (progress appears in status bar). Then Visualize.
5. Use toolbar buttons or menu for zoom, selection, exporting CSV, or clearing logs.
6. Open the Settings dialog (toolbar/settings icon or menu) to adjust detection parameters, visualization DPI/colormap/interpolation, theme (dark/light), font size, and debug flag.
7. Toggle “Enable Debug Logging” in the Options menu to show/hide the log dock and capture stdout/stderr.

Results CSV files appear in `results/`. Log output streams to the on‑screen log dock (when debug enabled) and always to `logs/novaloom.log` (rotating handler, ~1MB per file, 3 backups). Verbose Matplotlib font manager debug lines are suppressed for readability.

### Configuration (Lua Settings)
Persistent settings live in `config/settings.lua` and are loaded / saved automatically. Example:
```lua
settings = {
   debug = true,
   fits_file_path = '',
   analysis = {
      star_detection = {
         fwhm = 2.5,
         threshold_factor = 5.0,
      },
      visualization = {
         max_sources_display = 99,
         dpi = 99,
         interpolation = 'bilinear',
         colormap = 'viridis',
      },
   },
   ui = {
      theme = 'dark',      -- 'dark' or 'light'
      font_size = 10,
      window_size = { 800, 600 },
   },
}
```
You can edit this file manually (ensure valid Lua syntax) or rely on the in‑app Settings dialog which safely merges and rewrites the file.

Notable behaviors:
- Changes via the dialog are serialized atomically (full table rewrite with validation).
- Window size is preserved between sessions.
- Debug toggle updates log visibility & stdout capture immediately.

### Performance Metrics
The application logs timing for major UI actions (prefixed `PERF`) and zoom operations. These appear in the log dock / log file to help diagnose slow operations.

### For Script Users (Headless / CLI)

If you prefer scripted workflows or headless runs, use the existing modular scripts (independent of the GUI):

```
astro_analysis/
├── config/                    # Configuration settings
│   └── settings.py           # Edit this to configure your analysis
└── scripts/                  # Run these scripts to perform analysis
    ├── main.py              # Run this for complete analysis
    ├── load_fits.py         # Run this to load and check FITS files
    ├── display_section.py   # Run this to view image sections
    ├── detect_stars.py      # Run this to detect stars
    ├── calculate_stats.py   # Run this for statistical analysis
    ├── visualize_stars.py   # Run this to visualize stars
    └── visualize_3d.py      # Run this for 3D visualization
```

### For Developers (Extending the Code)

If you want to modify or extend the codebase, you'll also work with these internal modules:

```
astro_analysis/
├── data_processing/          # Core data processing functions
│   ├── fits_loader.py       # FITS file loading
│   ├── star_detection.py    # Star detection
│   └── simbad_query.py      # Simbad database interaction
├── utils/                    # Utility functions
│   ├── warnings.py          # Warning configuration
│   └── test_imports.py      # Import testing utility
└── visualization/            # Visualization functions
    └── plotting.py          # Plotting utilities
```

### Running the Analysis (CLI Scripts)

1. **Prepare your data**
   - Place your FITS file in the `Data` directory
   - Default location: `Data/Light_M42_180.0s_Bin1_0016.fit`
   - Supported formats: Standard FITS files with WCS information

2. **Configure settings** (optional)
   For scripts you can still directly modify parameters inside individual script files or migrate them into the Lua settings file and load them programmatically. (Legacy `settings.py` references have been superseded by `config/settings.lua` in the GUI.)

3. **Run the complete analysis**
   ```bash
   # From the project root directory
   python -m astro_analysis.scripts.main
   ```

4. **Run individual scripts**
   ```bash
   # Load and display FITS file
   python -m astro_analysis.scripts.load_fits

   # Display a section of the image
   python -m astro_analysis.scripts.display_section

   # Detect stars
   python -m astro_analysis.scripts.detect_stars

   # Visualize stars
   python -m astro_analysis.scripts.visualize_stars

   # Create 3D visualization
   python -m astro_analysis.scripts.visualize_3d
   ```

### Understanding the Output

The analysis generates several output files:
- `detected_stars.csv`: List of detected sources with coordinates
- `annotated_stars.png`: Visualization of detected stars
- `image_section.png`: Sample section of the image
- Various statistical outputs in the console

## 🔧 Troubleshooting

### GUI Specific
| Issue | Tips |
|-------|------|
| Log dock missing | Enable debug logging (Options menu) |
| Settings not persisting | Check `config/settings.lua` for syntax errors (no trailing commas) |
| Theme not changing | Ensure you click OK in the Settings dialog; invalid theme falls back to dark |
| Excessive log noise | Font manager spam is suppressed; toggle debug off to reduce remaining noise |

### Common Issues (Core)

1. **Import Errors**
   - Ensure you're running commands from the project root directory
   - Verify your virtual environment is activated
   - Run `python -m astro_analysis.utils.test_imports` to diagnose import issues

2. **FITS File Issues**
   - Verify the FITS file has valid WCS (if required by downstream steps)
   - Check file permissions / path correctness
   - Confirm path stored in `settings.lua` (fits_file_path) if relying on persistence

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
- All contributors who have helped improve this project

---

For more detailed information about specific features or advanced usage, explore module docstrings, or open an issue with your scenario and environment details.