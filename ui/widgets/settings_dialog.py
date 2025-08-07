"""
Settings dialog for NovaLoom application.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDoubleSpinBox, QSpinBox, QComboBox, QDialogButtonBox)


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
