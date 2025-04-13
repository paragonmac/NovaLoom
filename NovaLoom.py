from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QLabel, QFrame, QSplitter,
                             QTabWidget, QStatusBar, QDialog, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                             QLineEdit, QDialogButtonBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import qdarkstyle  # For dark theme support
import lupa  # Lua interpreter
import os

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
        
        # Load Lua settings
        self.lua = lupa.LuaRuntime()
        with open("astro_analysis/config/settings.lua", "r") as f:
            self.settings = self.lua.execute(f.read())
        
        self.setWindowTitle("NovaLoom - Astronomical Image Analysis")
        self.setMinimumSize(*self.settings["ui"]["window_size"])
        
        # Set application style based on theme
        if self.settings["ui"]["theme"] == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet())
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
        content_splitter = QSplitter(Qt.Horizontal)
        
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
        
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setIcon(QIcon("icons/visualize.png"))
        self.visualize_button.setMinimumHeight(40)
        
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
        
        # Add panels to splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setStretchFactor(1, 2)  # Right panel gets more space
        
        # Add splitter to main layout
        layout.addWidget(content_splitter)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Connect signals
        self.load_button.clicked.connect(self.load_fits)
        self.analyze_button.clicked.connect(self.analyze)
        self.visualize_button.clicked.connect(self.visualize)
        
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
            # Load and process FITS file
            self.statusBar.showMessage("Ready")
            
    def analyze(self):
        self.statusBar.showMessage("Analyzing...")
        # Run analysis with current settings
        self.statusBar.showMessage("Analysis complete")
        
    def visualize(self):
        self.statusBar.showMessage("Updating visualization...")
        # Update visualization with current settings
        self.canvas.draw()
        self.statusBar.showMessage("Ready")

if __name__ == "__main__":
    app = QApplication([])
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = AstroAnalysisUI()
    window.show()
    app.exec()
