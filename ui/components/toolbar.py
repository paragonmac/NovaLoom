"""
Toolbar component for the main window.
"""
from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon


class ToolbarManager:
    """Manages toolbar creation and button state"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbar = None
        
        # Zoom buttons
        self.zoom_in_button = None
        self.zoom_out_button = None
        self.reset_zoom_button = None
        
        # Selection buttons
        self.selection_toggle = None
        self.reset_selection = None
        
        # Other buttons
        self.export_data_button = None
    
    def create_toolbar(self, callbacks):
        """Create and configure the toolbar"""
        self.toolbar = self.main_window.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Add toolbar actions
        load_action = self.toolbar.addAction("Load")
        load_action.setIcon(QIcon("icons/load.png"))
        load_action.triggered.connect(callbacks.get('load_fits'))
        
        analyze_action = self.toolbar.addAction("Analyze")
        analyze_action.setIcon(QIcon("icons/analyze.png"))
        analyze_action.triggered.connect(callbacks.get('analyze'))
        
        self.toolbar.addSeparator()
        
        # Add zoom controls
        self.zoom_in_button = QToolButton()
        self.zoom_in_button.setIcon(QIcon("ui/NL_ZOOM_IN.png"))
        self.zoom_in_button.setToolTip("Enable Zoom In Mode")
        self.zoom_in_button.setCheckable(True)
        self.zoom_in_button.clicked.connect(callbacks.get('toggle_zoom_in'))
        self.toolbar.addWidget(self.zoom_in_button)
        
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setIcon(QIcon("ui/NL_ZOOM_OUT.png"))
        self.zoom_out_button.setToolTip("Enable Zoom Out Mode")
        self.zoom_out_button.setCheckable(True)
        self.zoom_out_button.clicked.connect(callbacks.get('toggle_zoom_out'))
        self.toolbar.addWidget(self.zoom_out_button)
        
        self.reset_zoom_button = QToolButton()
        self.reset_zoom_button.setIcon(QIcon("ui/NL_ZOOM_RESET.png"))
        self.reset_zoom_button.setToolTip("Reset Zoom")
        self.reset_zoom_button.clicked.connect(callbacks.get('reset_zoom'))
        self.toolbar.addWidget(self.reset_zoom_button)
        
        self.toolbar.addSeparator()
        
        # Add selection mode toggle
        self.selection_toggle = QToolButton()
        self.selection_toggle.setCheckable(True)
        self.selection_toggle.setIcon(QIcon("icons/select.png"))
        self.selection_toggle.setToolTip("Toggle Selection Mode")
        self.selection_toggle.clicked.connect(callbacks.get('toggle_selection'))
        self.toolbar.addWidget(self.selection_toggle)
        
        # Add reset selection button
        self.reset_selection = QToolButton()
        self.reset_selection.setIcon(QIcon("icons/reset.png"))
        self.reset_selection.setToolTip("Reset Selection")
        self.reset_selection.clicked.connect(callbacks.get('reset_source_selection'))
        self.toolbar.addWidget(self.reset_selection)
        
        # Add export data button
        self.export_data_button = QToolButton()
        self.export_data_button.setIcon(QIcon("icons/export.png"))
        self.export_data_button.setToolTip("Export Data")
        self.export_data_button.clicked.connect(callbacks.get('export_data'))
        self.toolbar.addWidget(self.export_data_button)
        
        self.toolbar.addSeparator()
        
        settings_action = self.toolbar.addAction("Settings")
        settings_action.setIcon(QIcon("icons/settings.png"))
        settings_action.triggered.connect(callbacks.get('show_settings'))
        
        self.toolbar.addSeparator()
        
        clear_log_action = self.toolbar.addAction("Clear Log")
        clear_log_action.setIcon(QIcon("icons/clear.png"))
        clear_log_action.triggered.connect(callbacks.get('clear_log'))
    
    def set_active_mode(self, mode):
        """Set the active mode and update button states"""
        # Reset all buttons
        self.zoom_in_button.setChecked(False)
        self.zoom_out_button.setChecked(False)
        self.selection_toggle.setChecked(False)
        
        # Set new mode
        if mode == 'zoom_in':
            self.zoom_in_button.setChecked(True)
        elif mode == 'zoom_out':
            self.zoom_out_button.setChecked(True)
        elif mode == 'select':
            self.selection_toggle.setChecked(True)
