import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

os.environ['QT_API'] = 'pyside6'  # Force PySide6

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="qdarkstyle")

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QLabel, QFrame, QSplitter,
                             QTabWidget, QStatusBar, QDialog, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                             QLineEdit, QDialogButtonBox, QTextEdit, QDockWidget,
                             QProgressBar, QToolButton, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QSize, QObject, Signal, QThread, Slot, QTimer, QDateTime
from PySide6.QtGui import QIcon, QPalette, QColor, QTextCursor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.widgets import RectangleSelector
import qdarkstyle  # For dark theme support
import lupa  # Lua interpreter
import logging
from io import StringIO
import numpy as np
import pandas as pd
from astropy.wcs import WCS
from astropy.io.fits import Header

# Import project modules
from astro_analysis.utils.io import read_fits
from astro_analysis.data_processing.star_detection import detect_sources
from astro_analysis.visualization.plotting import plot_image_with_labels

class LogStream(QObject):
    """Custom stream for redirecting stdout/stderr to the log window"""
    newText = Signal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass

class LogWindow(QTextEdit):
    """Custom log window widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setMaximumHeight(150)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                border: 1px solid #3c3c3c;
            }
        """)
        
    def append(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("NovaLoom Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Create form layout for settings
        form_layout = QFormLayout()
        
        # File paths
        self.fits_path = QLineEdit(settings["fits_file_path"])
        form_layout.addRow("FITS File Path:", self.fits_path)
        
        # Star detection settings
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setValue(settings["analysis"]["star_detection"]["fwhm"])
        self.fwhm.setRange(0.1, 10.0)
        form_layout.addRow("FWHM:", self.fwhm)
        
        self.threshold = QDoubleSpinBox()
        self.threshold.setValue(settings["analysis"]["star_detection"]["threshold_factor"])
        self.threshold.setRange(1.0, 20.0)
        form_layout.addRow("Threshold Factor:", self.threshold)
        
        # Visualization settings
        self.dpi = QSpinBox()
        self.dpi.setValue(settings["analysis"]["visualization"]["dpi"])
        self.dpi.setRange(72, 600)
        form_layout.addRow("DPI:", self.dpi)
        
        self.colormap = QComboBox()
        self.colormap.addItems(["viridis", "plasma", "inferno", "magma", "cividis"])
        self.colormap.setCurrentText(settings["analysis"]["visualization"]["colormap"])
        form_layout.addRow("Colormap:", self.colormap)
        
        # Source display limit
        self.max_sources = QSpinBox()
        self.max_sources.setValue(settings["analysis"]["visualization"]["max_sources_display"])
        self.max_sources.setRange(10, 1000)
        self.max_sources.setSingleStep(10)
        form_layout.addRow("Max Sources Display:", self.max_sources)
        
        # Interpolation setting
        self.interpolation = QComboBox()
        self.interpolation.addItems(["bilinear", "nearest"])
        self.interpolation.setCurrentText(settings["analysis"]["visualization"]["interpolation"])
        form_layout.addRow("Interpolation:", self.interpolation)
        
        # UI settings
        self.theme = QComboBox()
        self.theme.addItems(["dark", "light", "material"])
        self.theme.setCurrentText(settings["ui"]["theme"])
        form_layout.addRow("Theme:", self.theme)
        
        self.font_size = QSpinBox()
        self.font_size.setValue(settings["ui"]["font_size"])
        self.font_size.setRange(8, 24)
        form_layout.addRow("Font Size:", self.font_size)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_settings(self):
        return {
            "fits_file_path": self.fits_path.text(),
            "analysis": {
                "star_detection": {
                    "fwhm": self.fwhm.value(),
                    "threshold_factor": self.threshold.value()
                },
                "visualization": {
                    "dpi": self.dpi.value(),
                    "colormap": self.colormap.currentText(),
                    "max_sources_display": self.max_sources.value(),
                    "interpolation": self.interpolation.currentText()
                }
            },
            "ui": {
                "theme": self.theme.currentText(),
                "font_size": self.font_size.value()
            }
        }

class AnalysisWorker(QObject):
    """Worker class for running analysis in a separate thread"""
    finished = Signal()  # Signal emitted when analysis is complete
    error = Signal(str)  # Signal emitted when an error occurs
    progress = Signal(str)  # Signal for progress updates
    result = Signal(object)  # Signal for the analysis result

    def __init__(self, data, fwhm, threshold):
        super().__init__()
        self.data = data
        self.fwhm = fwhm
        self.threshold = threshold

    @Slot()
    def run(self):
        """Run the analysis"""
        try:
            self.progress.emit("Estimating background...")
            # Find sources
            sources_table = detect_sources(
                self.data,
                fwhm=self.fwhm,
                threshold=self.threshold
            )
            
            # Convert astropy Table to pandas DataFrame
            self.progress.emit("Converting results...")
            result_df = sources_table.to_pandas()
            
            self.result.emit(result_df)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))

class VisualizationWorker(QObject):
    """Worker class for handling visualization in a background thread"""
    finished = Signal()
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def run(self):
        """Run the visualization in the background"""
        try:
            self.parent.visualization_in_progress = True
            self.parent.visualize()
        finally:
            self.parent.visualization_in_progress = False
            self.finished.emit()

class AstroAnalysisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize data storage
        self.fits_data = None
        self.fits_header = None
        self.fits_wcs = None
        self.sources_df = None
        self.selected_sources_df = None
        self.current_fits_path = None
        
        # Initialize mode state
        self.active_mode = None  # None, 'zoom_in', 'zoom_out', or 'select'
        self.zoom_level = 1.0
        self.zoom_center = None
        self.original_limits = None  # Store original view limits
        
        # Initialize analysis thread
        self.analysis_thread = None
        self.analysis_worker = None
        
        # Initialize visualization thread
        self.visualization_thread = QThread()
        self.visualization_worker = None
        
        # Create results directory if it doesn't exist
        self.results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Set up logging
        self.log_window = LogWindow()
        self.setup_logging()
        
        # Initialize Lua environment and settings
        self.lua = lupa.LuaRuntime()
        self._init_lua_settings()
        
        self.setWindowTitle("NovaLoom - Astronomical Image Analysis")
        self.setMinimumSize(*self.settings["ui"]["window_size"])
        
        # Set application style based on theme
        if self.settings["ui"]["theme"] == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet())
        elif self.settings["ui"]["theme"] == "material":
            # Apply material theme
            pass
            
        # Track if visualization is in progress
        self.visualization_in_progress = False
        
        # Cache for plot data
        self.plot_cache = {
            'data': None,
            'sources': None,
            'cmap': None,
            'interpolation': None,
            'show_labels': None
        }
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        content_splitter = QSplitter(Qt.Vertical)  # Changed to vertical splitter
        
        # Create top splitter for main content
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Control buttons with icons
        self.load_button = QPushButton("Load FITS")
        self.load_button.setIcon(QIcon("icons/load.png"))
        self.load_button.setMinimumHeight(40)
        
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setIcon(QIcon("icons/analyze.png"))
        self.analyze_button.setMinimumHeight(40)
        self.analyze_button.setEnabled(False)  # Initially disabled
        
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setIcon(QIcon("icons/visualize.png"))
        self.visualize_button.setMinimumHeight(40)
        self.visualize_button.setEnabled(False)  # Initially disabled
        
        # Analysis settings group
        settings_group = QFrame()
        settings_group.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Analysis Settings"))
        
        # Add current settings display
        self.settings_label = QLabel()
        self.update_settings_display()
        settings_layout.addWidget(self.settings_label)
        
        left_layout.addWidget(self.load_button)
        left_layout.addWidget(self.analyze_button)
        left_layout.addWidget(self.visualize_button)
        left_layout.addWidget(settings_group)
        left_layout.addStretch()
        
        # Right panel - Results
        right_panel = QTabWidget()
        
        # Visualization tab
        vis_tab = QWidget()
        vis_layout = QVBoxLayout(vis_tab)
        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        vis_layout.addWidget(self.canvas)
        right_panel.addTab(vis_tab, "Visualization")
        
        # Data tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        # Create table widget for data display
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                gridline-color: #3c3c3c;
                alternate-background-color: #2d2d2d;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 4px;
                border: 1px solid #3c3c3c;
            }
        """)
        data_layout.addWidget(self.data_table)
        right_panel.addTab(data_tab, "Data")
        
        # Add panels to top splitter
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setStretchFactor(1, 2)  # Right panel gets more space
        
        # Add log window at the bottom
        self.log_dock = QDockWidget("Log", self)
        self.log_dock.setWidget(self.log_window)
        self.log_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | 
                           QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        
        # Add top splitter to main content splitter
        content_splitter.addWidget(top_splitter)
        
        # Add content splitter to main layout
        layout.addWidget(content_splitter)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Connect signals
        self.load_button.clicked.connect(self.load_fits)
        self.analyze_button.clicked.connect(self.analyze)
        self.visualize_button.clicked.connect(self.visualize)
        
        # Set up resize handling
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_resize)
        self.is_resizing = False
        
    def setup_logging(self):
        """Set up logging to capture stdout/stderr and redirect to log window"""
        # Create custom stream
        self.log_stream = LogStream()
        self.log_stream.newText.connect(self.log_window.append)
        
        # Redirect stdout and stderr
        sys.stdout = self.log_stream
        sys.stderr = self.log_stream
        
        # Set up Python logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=self.log_stream
        )
        
        # Log startup message
        self.log_window.append("NovaLoom started\n")
        
    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Add toolbar actions
        load_action = toolbar.addAction("Load")
        load_action.setIcon(QIcon("icons/load.png"))
        load_action.triggered.connect(self.load_fits)
        
        analyze_action = toolbar.addAction("Analyze")
        analyze_action.setIcon(QIcon("icons/analyze.png"))
        analyze_action.triggered.connect(self.analyze)
        
        toolbar.addSeparator()
        
        # Add zoom controls
        self.zoom_in_button = QToolButton()
        self.zoom_in_button.setIcon(QIcon("icons/zoom_in.png"))
        self.zoom_in_button.setToolTip("Enable Zoom In Mode")
        self.zoom_in_button.setCheckable(True)
        self.zoom_in_button.clicked.connect(self.toggle_zoom_in)
        toolbar.addWidget(self.zoom_in_button)
        
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setIcon(QIcon("icons/zoom_out.png"))
        self.zoom_out_button.setToolTip("Enable Zoom Out Mode")
        self.zoom_out_button.setCheckable(True)
        self.zoom_out_button.clicked.connect(self.toggle_zoom_out)
        toolbar.addWidget(self.zoom_out_button)
        
        self.reset_zoom_button = QToolButton()
        self.reset_zoom_button.setIcon(QIcon("icons/zoom_reset.png"))
        self.reset_zoom_button.setToolTip("Reset Zoom")
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        toolbar.addWidget(self.reset_zoom_button)
        
        toolbar.addSeparator()
        
        # Add selection mode toggle
        self.selection_toggle = QToolButton()
        self.selection_toggle.setCheckable(True)
        self.selection_toggle.setIcon(QIcon("icons/select.png"))
        self.selection_toggle.setToolTip("Toggle Selection Mode")
        self.selection_toggle.clicked.connect(self.toggle_selection)
        toolbar.addWidget(self.selection_toggle)
        
        # Add reset selection button
        self.reset_selection = QToolButton()
        self.reset_selection.setIcon(QIcon("icons/reset.png"))
        self.reset_selection.setToolTip("Reset Selection")
        self.reset_selection.clicked.connect(self.reset_source_selection)
        toolbar.addWidget(self.reset_selection)
        
        # Add export data button
        self.export_data_button = QToolButton()
        self.export_data_button.setIcon(QIcon("icons/export.png"))
        self.export_data_button.setToolTip("Export Data")
        self.export_data_button.clicked.connect(self.export_data)
        toolbar.addWidget(self.export_data_button)
        
        toolbar.addSeparator()
        
        settings_action = toolbar.addAction("Settings")
        settings_action.setIcon(QIcon("icons/settings.png"))
        settings_action.triggered.connect(self.show_settings)
        
        toolbar.addSeparator()
        
        clear_log_action = toolbar.addAction("Clear Log")
        clear_log_action.setIcon(QIcon("icons/clear.png"))
        clear_log_action.triggered.connect(self.clear_log)
        
    def update_settings_display(self):
        # Truncate long file paths
        fits_path = self.settings['fits_file_path']
        if len(fits_path) > 50:
            fits_path = "..." + fits_path[-47:]  # Show last 47 chars with ellipsis
        
        settings_text = f"""
        FITS File: {fits_path}
        FWHM: {self.settings['analysis']['star_detection']['fwhm']}
        Threshold: {self.settings['analysis']['star_detection']['threshold_factor']}
        DPI: {self.settings['analysis']['visualization']['dpi']}
        Colormap: {self.settings['analysis']['visualization']['colormap']}
        Interpolation: {self.settings['analysis']['visualization']['interpolation']}
        """
        self.settings_label.setText(settings_text)
        self.settings_label.setWordWrap(True)  # Enable word wrapping
        self.settings_label.setToolTip(self.settings['fits_file_path'])  # Show full path on hover
        
    def _init_lua_settings(self):
        """Initialize the Lua settings table"""
        try:
            # Create the settings table in Lua
            self.lua.execute("""
                settings = {
                    fits_file_path = "",
                    analysis = {
                        star_detection = {
                            fwhm = 2.5,
                            threshold_factor = 5.0
                        },
                        visualization = {
                            dpi = 100,
                            colormap = "viridis",
                            max_sources_display = 100,
                            interpolation = "bilinear"
                        }
                    },
                    ui = {
                        theme = "dark",
                        font_size = 10,
                        window_size = {800, 600}
                    }
                }
            """)
            
            # Load settings from file if it exists
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.lua")
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r") as f:
                        self.lua.execute(f.read())
                except Exception as e:
                    logging.warning(f"Could not load settings file: {str(e)}")
            
            # Get the settings table
            self.settings = self.lua.execute("settings")
            
        except Exception as e:
            logging.error(f"Error initializing settings: {str(e)}")
            # Create a Python dictionary as fallback
            self.settings = {
                "fits_file_path": "",
                "analysis": {
                    "star_detection": {
                        "fwhm": 2.5,
                        "threshold_factor": 5.0
                    },
                    "visualization": {
                        "dpi": 100,
                        "colormap": "viridis",
                        "max_sources_display": 100,
                        "interpolation": "bilinear"
                    }
                },
                "ui": {
                    "theme": "dark",
                    "font_size": 10,
                    "window_size": [800, 600]
                }
            }

    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            
            try:
                # Update settings in Lua
                for key, value in new_settings.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, dict):
                                for subsubkey, subsubvalue in subvalue.items():
                                    if isinstance(subsubvalue, str):
                                        self.lua.execute(f"settings['{key}']['{subkey}']['{subsubkey}'] = '{subsubvalue}'")
                                    else:
                                        self.lua.execute(f"settings['{key}']['{subkey}']['{subsubkey}'] = {subsubvalue}")
                            else:
                                if isinstance(subvalue, str):
                                    self.lua.execute(f"settings['{key}']['{subkey}'] = '{subvalue}'")
                                else:
                                    self.lua.execute(f"settings['{key}']['{subkey}'] = {subvalue}")
                    else:
                        if isinstance(value, str):
                            self.lua.execute(f"settings['{key}'] = '{value}'")
                        else:
                            self.lua.execute(f"settings['{key}'] = {value}")
                
                # Save settings to file
                settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.lua")
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                
                with open(settings_path, "w") as f:
                    f.write("settings = {\n")
                    for key, value in new_settings.items():
                        if isinstance(value, dict):
                            f.write(f"    {key} = {{\n")
                            for subkey, subvalue in value.items():
                                if isinstance(subvalue, dict):
                                    f.write(f"        {subkey} = {{\n")
                                    for subsubkey, subsubvalue in subvalue.items():
                                        if isinstance(subsubvalue, str):
                                            f.write(f"            {subsubkey} = '{subsubvalue}',\n")
                                        else:
                                            f.write(f"            {subsubkey} = {subsubvalue},\n")
                                    f.write("        },\n")
                                else:
                                    if isinstance(subvalue, str):
                                        f.write(f"        {subkey} = '{subvalue}',\n")
                                    else:
                                        f.write(f"        {subkey} = {subvalue},\n")
                            f.write("    },\n")
                        else:
                            if isinstance(value, str):
                                f.write(f"    {key} = '{value}',\n")
                            else:
                                f.write(f"    {key} = {value},\n")
                    f.write("}\n")
                
                # Reload settings from Lua
                self.settings = self.lua.execute("settings")
                
            except Exception as e:
                logging.error(f"Error updating settings: {str(e)}")
                # Update Python settings as fallback
                self.settings = new_settings
            
            # Update display and apply changes regardless of Lua success
            self.update_settings_display()
            
            # Apply theme changes
            if self.settings["ui"]["theme"] == "dark":
                self.setStyleSheet(qdarkstyle.load_stylesheet())
            elif self.settings["ui"]["theme"] == "material":
                # Apply material theme
                pass
            
            # Update font size
            self.setStyleSheet(f"font-size: {self.settings['ui']['font_size']}px;")
        
    def load_fits(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FITS File", "", "FITS Files (*.fit *.fits)"
        )
        if file_path:
            self.current_fits_path = file_path
            self.settings["fits_file_path"] = file_path
            self.update_settings_display()
            self.statusBar.showMessage(f"Loading {file_path}...")
            logging.info(f"Loading FITS file: {file_path}")
            
            try:
                # Load FITS data first
                self.fits_data, self.fits_header, self.fits_wcs = read_fits(file_path)
                logging.info("FITS file loaded successfully")
                
                # Check if we have cached results for this file
                results_path = self._get_results_path(file_path)
                if os.path.exists(results_path):
                    logging.info(f"Loading cached results from {results_path}")
                    self.sources_df = pd.read_csv(results_path)
                    self.update_data_table()  # Update the data table
                    self.analyze_button.setEnabled(False)  # Disable analyze since we already have results
                    self.visualize_button.setEnabled(True)  # Enable visualize
                    self.statusBar.showMessage("Loaded cached results")
                    # Visualize immediately since we have both data and results
                    self.visualize()
                    return
                
                # If no cached results, enable analyze button
                self.analyze_button.setEnabled(True)
                self.visualize_button.setEnabled(False)
                self.sources_df = None  # Clear previous analysis
                self.update_data_table()  # Clear the data table
                
                self.statusBar.showMessage("Ready")
            except Exception as e:
                logging.error(f"Error loading FITS file: {str(e)}")
                self.statusBar.showMessage("Error loading file")
                self.analyze_button.setEnabled(False)
                self.visualize_button.setEnabled(False)
            
    def _get_results_path(self, fits_path):
        """Get the path for cached results based on the FITS file path"""
        filename = os.path.basename(fits_path)
        base_name = os.path.splitext(filename)[0]
        return os.path.join(self.results_dir, f"{base_name}_sources.csv")

    def analyze(self):
        if self.fits_data is None:
            logging.error("No FITS data loaded")
            self.statusBar.showMessage("No FITS data loaded")
            return
            
        # Disable analyze button during analysis
        self.analyze_button.setEnabled(False)
        self.statusBar.showMessage("Analyzing...")
        logging.info("Starting analysis...")
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar.addPermanentWidget(self.progress_bar)
        
        # Get analysis settings
        fwhm = self.settings["analysis"]["star_detection"]["fwhm"]
        threshold = self.settings["analysis"]["star_detection"]["threshold_factor"]
        
        # Create worker and thread
        self.analysis_worker = AnalysisWorker(self.fits_data, fwhm, threshold)
        self.analysis_thread = QThread()
        
        # Move worker to thread
        self.analysis_worker.moveToThread(self.analysis_thread)
        
        # Connect signals
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        self.analysis_worker.error.connect(self.handle_analysis_error)
        self.analysis_worker.progress.connect(self.update_analysis_progress)
        self.analysis_worker.result.connect(self.handle_analysis_result)
        
        # Start the thread
        self.analysis_thread.start()
    
    def handle_analysis_error(self, error_msg):
        """Handle analysis errors"""
        logging.error(f"Error during analysis: {error_msg}")
        self.statusBar.showMessage("Analysis failed")
        self.analyze_button.setEnabled(True)
        self.progress_bar.hide()
        self.statusBar.removeWidget(self.progress_bar)
    
    def update_analysis_progress(self, message):
        """Update progress message"""
        logging.info(message)
        self.statusBar.showMessage(message)
    
    def handle_analysis_result(self, result_df):
        """Handle successful analysis results"""
        self.sources_df = result_df
        num_sources = len(self.sources_df)
        logging.info(f"Analysis complete. Found {num_sources} sources.")
        
        # Save results to CSV
        try:
            results_path = self._get_results_path(self.current_fits_path)
            self.sources_df.to_csv(results_path, index=False)
            logging.info(f"Saved analysis results to {results_path}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")
        
        # Update the data table
        self.update_data_table()
        
        # Enable visualize button
        self.visualize_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.statusBar.showMessage("Analysis complete")
        
        # Remove progress bar
        self.progress_bar.hide()
        self.statusBar.removeWidget(self.progress_bar)

    def toggle_zoom_in(self):
        """Toggle zoom in mode"""
        if self.zoom_in_button.isChecked():
            self.set_active_mode('zoom_in')
        else:
            self.set_active_mode(None)

    def toggle_zoom_out(self):
        """Toggle zoom out mode"""
        if self.zoom_out_button.isChecked():
            self.set_active_mode('zoom_out')
        else:
            self.set_active_mode(None)

    def toggle_selection(self):
        """Toggle selection mode"""
        if self.selection_toggle.isChecked():
            self.set_active_mode('select')
        else:
            self.set_active_mode(None)

    def set_active_mode(self, mode):
        """Set the active mode and update UI accordingly"""
        # Reset all buttons
        self.zoom_in_button.setChecked(False)
        self.zoom_out_button.setChecked(False)
        self.selection_toggle.setChecked(False)
        
        # Set new mode
        self.active_mode = mode
        
        # Update button states and status message
        if mode == 'zoom_in':
            self.zoom_in_button.setChecked(True)
            self.statusBar.showMessage("Zoom in mode active - click on image to zoom in")
            logging.info("Zoom in mode activated")
        elif mode == 'zoom_out':
            self.zoom_out_button.setChecked(True)
            self.statusBar.showMessage("Zoom out mode active - click on image to zoom out")
            logging.info("Zoom out mode activated")
        elif mode == 'select':
            self.selection_toggle.setChecked(True)
            self.statusBar.showMessage("Selection mode active - drag to select area")
            logging.info("Selection mode activated")
            # Update visualization to show selection mode
            self.visualize()
        else:
            self.active_mode = None
            self.statusBar.showMessage("Ready")
            logging.info("All modes deactivated")
            # Update visualization when deactivating modes
            self.visualize()
    
    def on_select(self, eclick, erelease):
        """Handle rectangle selection"""
        if self.active_mode != 'select' or self.sources_df is None:
            return
            
        # Get selection coordinates
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Ensure coordinates are in the correct order
        xmin, xmax = min(x1, x2), max(x1, x2)
        ymin, ymax = min(y1, y2), max(y1, y2)
        
        # Filter sources within the selection
        mask = (
            (self.sources_df['xcentroid'] >= xmin) &
            (self.sources_df['xcentroid'] <= xmax) &
            (self.sources_df['ycentroid'] >= ymin) &
            (self.sources_df['ycentroid'] <= ymax)
        )
        
        self.selected_sources_df = self.sources_df[mask]
        
        # Update visualization with selected sources
        self.visualize()
        
        # Log selection
        num_selected = len(self.selected_sources_df)
        total_sources = len(self.sources_df)
        logging.info(f"Selected {num_selected} of {total_sources} sources")
        self.statusBar.showMessage(f"Selected {num_selected} sources")

    def on_click(self, event):
        """Handle mouse clicks for zooming"""
        if event.inaxes is None or self.fits_data is None or self.active_mode is None:
            return
            
        if self.active_mode == 'zoom_in':
            self.zoom_center = (event.xdata, event.ydata)
            self.zoom_level = 2.0  # Fixed 2x zoom
            self.update_zoom()
            logging.info("Zoomed in 2x")
        elif self.active_mode == 'zoom_out':
            self.zoom_center = (event.xdata, event.ydata)
            self.zoom_level = 0.5  # Fixed 0.5x zoom (2x out)
            self.update_zoom()
            logging.info("Zoomed out 2x")
    
    def reset_zoom(self):
        """Reset zoom to show entire image"""
        if self.fits_data is None:
            return
            
        self.zoom_level = 1.0
        self.zoom_center = None
        self.set_active_mode(None)  # Deactivate all modes
        
        if self.original_limits is not None:
            ax = self.figure.gca()
            ax.set_xlim(self.original_limits[0])
            ax.set_ylim(self.original_limits[1])
            self.canvas.draw()
            logging.info("Zoom reset to full view")
            self.statusBar.showMessage("Zoom reset to full view")
    
    def update_zoom(self):
        """Update the plot with current zoom level"""
        if self.fits_data is None:
            return
            
        ax = self.figure.gca()
        
        # Get current axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Calculate new limits based on zoom level and center
        if self.zoom_center is not None:
            x_center, y_center = self.zoom_center
            x_range = (xlim[1] - xlim[0]) / self.zoom_level
            y_range = (ylim[1] - ylim[0]) / self.zoom_level
            
            new_xlim = (x_center - x_range/2, x_center + x_range/2)
            new_ylim = (y_center - y_range/2, y_center + y_range/2)
        else:
            # If no center point, zoom around the center of the current view
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) / self.zoom_level
            y_range = (ylim[1] - ylim[0]) / self.zoom_level
            
            new_xlim = (x_center - x_range/2, x_center + x_range/2)
            new_ylim = (y_center - y_range/2, y_center + y_range/2)
        
        # Set new limits
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        
        # Redraw the canvas
        self.canvas.draw()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        # Clear the current image
        if self.figure is not None:
            self.figure.clear()
            self.canvas.draw()
            self.canvas.flush_events()
        
        # Let Qt handle the resize
        super().resizeEvent(event)
        
        # Schedule the redraw
        if self.fits_data is not None and self.sources_df is not None:
            self.resize_timer.start(100)  # Wait 100ms before redrawing

    def _handle_resize(self):
        """Handle the actual resize after it's complete"""
        if self.fits_data is not None and self.sources_df is not None:
            # Force a complete redraw
            self.plot_cache = {
                'data': None,
                'sources': None,
                'cmap': None,
                'interpolation': None,
                'show_labels': None
            }
            self.visualize(force_redraw=True)

    def visualize(self, force_redraw=False):
        """Visualize the current data"""
        if self.fits_data is None or self.sources_df is None:
            logging.warning("Cannot visualize: FITS data or source data missing")
            self.statusBar.showMessage("Data missing for visualization")
            return
            
        if self.visualization_in_progress:
            return
            
        self.visualization_in_progress = True
        self.statusBar.showMessage("Updating visualization...")
        logging.info("Updating visualization...")
        
        try:
            # Get visualization settings
            cmap = self.settings["analysis"]["visualization"]["colormap"]
            max_sources = self.settings["analysis"]["visualization"]["max_sources_display"]
            interpolation = self.settings["analysis"]["visualization"]["interpolation"]
            
            # Use selected sources if available, otherwise use all sources
            display_df = self.selected_sources_df if self.selected_sources_df is not None else self.sources_df
            
            # Limit the number of sources to display
            if len(display_df) > max_sources:
                display_df = display_df.head(max_sources)
                logging.info(f"Displaying {max_sources} of {len(display_df)} sources")
            
            # Show labels if we have selected sources or are in selection mode
            show_labels = self.selected_sources_df is not None or self.active_mode == 'select'
            
            # Check if we need to redraw
            needs_redraw = force_redraw or (
                self.plot_cache['data'] is None or
                self.plot_cache['sources'] is not display_df or
                self.plot_cache['cmap'] != cmap or
                self.plot_cache['interpolation'] != interpolation or
                self.plot_cache['show_labels'] != show_labels
            )
            
            if needs_redraw:
                # Clear the figure
                self.figure.clear()
                
                # Create plot with improved interpolation
                plot_image_with_labels(
                    data=self.fits_data,
                    sources_df=display_df,
                    wcs=self.fits_wcs,
                    header=self.fits_header,
                    fits_file_path=self.settings["fits_file_path"],
                    cmap=cmap,
                    fig=self.figure,
                    interpolation=interpolation,
                    show_labels=show_labels
                )
                
                # Store original limits for reset
                ax = self.figure.gca()
                self.original_limits = (ax.get_xlim(), ax.get_ylim())
                
                # Connect click event for zooming
                self.canvas.mpl_connect('button_press_event', self.on_click)
                
                # Add rectangle selector if in selection mode
                if self.active_mode == 'select':
                    self.rect_selector = RectangleSelector(
                        self.figure.gca(),
                        self.on_select,
                        useblit=True,
                        button=[1],  # Left mouse button
                        minspanx=5, minspany=5,  # Minimum size
                        spancoords='data',
                        interactive=True
                    )
                
                # Update cache
                self.plot_cache = {
                    'data': self.fits_data,
                    'sources': display_df,
                    'cmap': cmap,
                    'interpolation': interpolation,
                    'show_labels': show_labels
                }
            
            # Update canvas
            self.canvas.draw()
            self.statusBar.showMessage("Ready")
            logging.info("Visualization updated")
            
        except Exception as e:
            logging.error(f"Error during visualization: {str(e)}")
            self.statusBar.showMessage("Visualization failed")
        finally:
            self.visualization_in_progress = False

    def reset_source_selection(self):
        """Reset the source selection to show all sources"""
        if self.sources_df is not None:
            self.selected_sources_df = None
            self.visualize()
            self.statusBar.showMessage("Selection reset")
            logging.info("Source selection reset")
            self.set_active_mode(None)  # Deactivate all modes

    def clear_log(self):
        """Clears the content of the log window."""
        self.log_window.clear()
        logging.info("Log cleared.") # Optionally log the clear action

    def update_data_table(self):
        """Update the data table with current sources data"""
        if self.sources_df is None:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
            
        # Set up the table
        self.data_table.setRowCount(len(self.sources_df))
        self.data_table.setColumnCount(len(self.sources_df.columns))
        self.data_table.setHorizontalHeaderLabels(self.sources_df.columns)
        
        # Fill the table with data
        for i, row in self.sources_df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        # Resize columns to fit content
        self.data_table.resizeColumnsToContents()
        
        # Enable sorting
        self.data_table.setSortingEnabled(True)

    def export_data(self):
        """Export the current data to a CSV file"""
        if self.sources_df is None:
            self.statusBar.showMessage("No data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                self.sources_df.to_csv(file_path, index=False)
                self.statusBar.showMessage(f"Data exported to {file_path}")
                logging.info(f"Data exported to {file_path}")
            except Exception as e:
                self.statusBar.showMessage("Error exporting data")
                logging.error(f"Error exporting data: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = AstroAnalysisUI()
    window.show()
    app.exec()
