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
                             QLineEdit, QDialogButtonBox, QTextEdit, QDockWidget)
from PySide6.QtCore import Qt, QSize, QObject, Signal
from PySide6.QtGui import QIcon, QPalette, QColor, QTextCursor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg  # Use general Qt backend
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
                    "colormap": self.colormap.currentText()
                }
            },
            "ui": {
                "theme": self.theme.currentText(),
                "font_size": self.font_size.value()
            }
        }

class AstroAnalysisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize data storage
        self.fits_data = None
        self.fits_header = None
        self.fits_wcs = None
        self.sources_df = None
        
        # Set up logging
        self.log_window = LogWindow()
        self.setup_logging()
        
        # Load Lua settings
        self.lua = lupa.LuaRuntime()
        with open("astro_analysis/config/settings.lua", "r") as f:
            self.settings = self.lua.execute(f.read())
        
        self.setWindowTitle("NovaLoom - Astronomical Image Analysis")
        self.setMinimumSize(*self.settings["ui"]["window_size"])
        
        # Set application style based on theme
        if self.settings["ui"]["theme"] == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet())  # Use main qdarkstyle
        elif self.settings["ui"]["theme"] == "material":
            # Apply material theme
            pass
        
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
        # Add data table/view here
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
        
        settings_action = toolbar.addAction("Settings")
        settings_action.setIcon(QIcon("icons/settings.png"))
        settings_action.triggered.connect(self.show_settings)

        toolbar.addSeparator()

        clear_log_action = toolbar.addAction("Clear Log")
        clear_log_action.setIcon(QIcon("icons/clear.png")) # Assuming you have a clear icon
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
        """
        self.settings_label.setText(settings_text)
        self.settings_label.setWordWrap(True)  # Enable word wrapping
        self.settings_label.setToolTip(self.settings['fits_file_path'])  # Show full path on hover
        
    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            # Update settings
            self.settings.update(new_settings)
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
            self.settings["fits_file_path"] = file_path
            self.update_settings_display()
            self.statusBar.showMessage(f"Loading {file_path}...")
            logging.info(f"Loading FITS file: {file_path}")
            
            try:
                # Load FITS data
                self.fits_data, self.fits_header, self.fits_wcs = read_fits(file_path)
                logging.info("FITS file loaded successfully")
                
                # Enable analyze button and disable visualize button
                self.analyze_button.setEnabled(True)
                self.visualize_button.setEnabled(False)
                self.sources_df = None  # Clear previous analysis
                
                self.statusBar.showMessage("Ready")
            except Exception as e:
                logging.error(f"Error loading FITS file: {str(e)}")
                self.statusBar.showMessage("Error loading file")
                self.analyze_button.setEnabled(False)
                self.visualize_button.setEnabled(False)
            
    def analyze(self):
        if self.fits_data is None:
            logging.error("No FITS data loaded")
            self.statusBar.showMessage("No FITS data loaded")
            return
            
        self.statusBar.showMessage("Analyzing...")
        logging.info("Starting analysis...")
        
        try:
            # Get analysis settings
            fwhm = self.settings["analysis"]["star_detection"]["fwhm"]
            threshold = self.settings["analysis"]["star_detection"]["threshold_factor"]
            
            # Find sources
            sources_table = detect_sources(
                self.fits_data,
                fwhm=fwhm,
                threshold=threshold
            )
            
            # Convert astropy Table to pandas DataFrame
            self.sources_df = sources_table.to_pandas()
            
            num_sources = len(self.sources_df)
            logging.info(f"Analysis complete. Found {num_sources} sources.")
            
            # Enable visualize button
            self.visualize_button.setEnabled(True)
            self.statusBar.showMessage("Analysis complete")
            
        except Exception as e:
            logging.error(f"Error during analysis: {str(e)}")
            self.statusBar.showMessage("Analysis failed")
            self.visualize_button.setEnabled(False)
            
    def visualize(self):
        if self.fits_data is None or self.sources_df is None:
            logging.warning("Cannot visualize: FITS data or source data missing")
            self.statusBar.showMessage("Data missing for visualization")
            return
            
        self.statusBar.showMessage("Updating visualization...")
        logging.info("Updating visualization...")
        
        try:
            # Get visualization settings
            cmap = self.settings["analysis"]["visualization"]["colormap"]
            
            # Create plot
            plot_image_with_labels(
                data=self.fits_data,
                sources_df=self.sources_df,
                wcs=self.fits_wcs,
                header=self.fits_header,
                fits_file_path=self.settings["fits_file_path"],
                cmap=cmap,
                fig=self.figure
            )
            
            # Update canvas
            self.canvas.draw()
            self.statusBar.showMessage("Ready")
            logging.info("Visualization updated")
            
        except Exception as e:
            logging.error(f"Error during visualization: {str(e)}")
            self.statusBar.showMessage("Visualization failed")

    def clear_log(self):
        """Clears the content of the log window."""
        self.log_window.clear()
        logging.info("Log cleared.") # Optionally log the clear action

if __name__ == "__main__":
    app = QApplication([])
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = AstroAnalysisUI()
    window.show()
    app.exec()
