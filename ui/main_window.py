"""
Simplified main window that delegates to controllers and managers.
"""
import os
import sys
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QFrame, QSplitter,
                             QTabWidget, QStatusBar, QDialog, QDockWidget,
                             QProgressBar, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QTimer
import qdarkstyle

from ui.widgets.log_window import LogStream, LogWindow
from ui.widgets.settings_dialog import SettingsDialog
from ui.components.toolbar import ToolbarManager
from core.data_manager import DataManager
from core.controllers.analysis_controller import AnalysisController
from core.controllers.visualization_controller import VisualizationController
from core.settings_manager import SettingsManager
from core.enums import InteractionMode
from core.errors import FitsLoadError, ExportError, AnalysisError


class AstroAnalysisUI(QMainWindow):
    """Main application window - orchestrates components and controllers"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers and controllers
        self._init_managers()
        
        # Initialize UI
        self._init_ui()
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Initialize state
        self.active_mode = InteractionMode.NONE
        
        # Set up resize handling
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_resize)
    
    def _init_managers(self):
        """Initialize all managers and controllers"""
        # Set up logging
        self.log_window = LogWindow()
        self._setup_logging()
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Initialize data manager
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
        self.data_manager = DataManager(results_dir)
        
        # Initialize analysis controller
        self.analysis_controller = AnalysisController()
        self.analysis_controller.set_callbacks(
            on_error=self._handle_analysis_error,
            on_progress=self._update_analysis_progress,
            on_result=self._handle_analysis_result
        )
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NovaLoom - Astronomical Image Analysis")
        self.setMinimumSize(*self.settings["ui"]["window_size"])
        
        # Set application style based on theme
        self._apply_theme()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create toolbar
        self.toolbar_manager = ToolbarManager(self)
        self.toolbar_manager.create_toolbar(self._get_toolbar_callbacks())
        
        # Create main content area
        content_splitter = QSplitter(Qt.Vertical)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = self._create_control_panel()
        
        # Right panel - Visualization and data
        right_panel = self._create_results_panel()
        
        # Add panels to splitter
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setStretchFactor(1, 2)  # Right panel gets more space
        
        # Add log window at the bottom
        self.log_dock = QDockWidget("Log", self)
        self.log_dock.setWidget(self.log_window)
        self.log_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | 
                           QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        
        content_splitter.addWidget(top_splitter)
        layout.addWidget(content_splitter)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def _create_control_panel(self):
        """Create the left control panel"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Control buttons
        self.load_button = QPushButton("Load FITS")
        self.load_button.setMinimumHeight(40)
        
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setMinimumHeight(40)
        self.analyze_button.setEnabled(False)
        
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setMinimumHeight(40)
        self.visualize_button.setEnabled(False)
        
        # Settings display
        settings_group = QFrame()
        settings_group.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Analysis Settings"))
        
        self.settings_label = QLabel()
        self._update_settings_display()
        settings_layout.addWidget(self.settings_label)
        
        # Add to layout
        left_layout.addWidget(self.load_button)
        left_layout.addWidget(self.analyze_button)
        left_layout.addWidget(self.visualize_button)
        left_layout.addWidget(settings_group)
        left_layout.addStretch()
        
        return left_panel
    
    def _create_results_panel(self):
        """Create the right results panel"""
        right_panel = QTabWidget()
        
        # Visualization tab
        vis_tab = QWidget()
        vis_layout = QVBoxLayout(vis_tab)
        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        vis_layout.addWidget(self.canvas)
        right_panel.addTab(vis_tab, "Visualization")
        
        # Initialize visualization controller
        self.viz_controller = VisualizationController(self.figure, self.canvas)
        
        # Data tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self._apply_table_style()
        data_layout.addWidget(self.data_table)
        right_panel.addTab(data_tab, "Data")
        
        return right_panel
    
    def _setup_event_handlers(self):
        """Set up event handlers and signal connections"""
        # Button connections
        self.load_button.clicked.connect(self.load_fits)
        self.analyze_button.clicked.connect(self.analyze)
        self.visualize_button.clicked.connect(self.visualize)
        
        # Canvas click events
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)
    
    def _get_toolbar_callbacks(self):
        """Get callback dictionary for toolbar"""
        return {
            'load_fits': self.load_fits,
            'analyze': self.analyze,
            'cancel_analysis': self.cancel_analysis,
            'toggle_zoom_in': self.toggle_zoom_in,
            'toggle_zoom_out': self.toggle_zoom_out,
            'reset_zoom': self.reset_zoom,
            'toggle_selection': self.toggle_selection,
            'reset_source_selection': self.reset_source_selection,
            'export_data': self.export_data,
            'show_settings': self.show_settings,
            'clear_log': self.clear_log
        }
    
    # Event handler methods
    def load_fits(self):
        """Load a FITS file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FITS File", "", "FITS Files (*.fit *.fits)"
        )
        if file_path:
            self.statusBar.showMessage(f"Loading {file_path}...")
            logging.info(f"Loading FITS file: {file_path}")
            try:
                success, status = self.data_manager.load_fits_file(file_path)
            except FitsLoadError as e:
                self.statusBar.showMessage("Error loading file")
                logging.exception("FITS load failed")
                self.analyze_button.setEnabled(False)
                self.visualize_button.setEnabled(False)
                return
            
            if success:
                self.settings["fits_file_path"] = file_path
                self._update_settings_display()
                
                if status == "loaded_with_cache":
                    self._update_data_table()
                    self.analyze_button.setEnabled(False)
                    self.visualize_button.setEnabled(True)
                    self.statusBar.showMessage("Loaded cached results")
                    self.visualize()
                else:
                    self.analyze_button.setEnabled(True)
                    self.visualize_button.setEnabled(False)
                    self._update_data_table()
                    self.statusBar.showMessage("Ready")
            else:
                self.statusBar.showMessage("Error loading file")
                self.analyze_button.setEnabled(False)
                self.visualize_button.setEnabled(False)
    
    def analyze(self):
        """Start analysis"""
        success, message = self.analysis_controller.start_analysis(self.data_manager, self.settings)
        
        if success:
            self.analyze_button.setEnabled(False)
            self.statusBar.showMessage("Analyzing...")
            
            # Create progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.statusBar.addPermanentWidget(self.progress_bar)
        else:
            self.statusBar.showMessage(message)
    
    def visualize(self):
        """Update visualization"""
        success, message = self.viz_controller.visualize(
            self.data_manager, 
            self.settings, 
            active_mode=self.active_mode
        )
        self.statusBar.showMessage("Ready" if success else message)
    
    def toggle_zoom_in(self):
        """Toggle zoom in mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.ZOOM_IN) else InteractionMode.ZOOM_IN)
    
    def toggle_zoom_out(self):
        """Toggle zoom out mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.ZOOM_OUT) else InteractionMode.ZOOM_OUT)
    
    def toggle_selection(self):
        """Toggle selection mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.SELECT) else InteractionMode.SELECT)
    
    def reset_zoom(self):
        """Reset zoom"""
        if self.viz_controller.reset_zoom():
            # Exit zoom modes without forcing full re-visualization
            self.active_mode = None
            self.toolbar_manager.set_active_mode(None)
            self.statusBar.showMessage("Zoom reset to full view")
    
    def reset_source_selection(self):
        """Reset source selection"""
        self.data_manager.reset_selection()
        self._set_active_mode(None)
        self.visualize()
        self.statusBar.showMessage("Selection reset")
    
    def export_data(self):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                success, message = self.data_manager.export_data(file_path)
                self.statusBar.showMessage(message)
            except ExportError as e:
                self.statusBar.showMessage(str(e))
                logging.exception("Export failed")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings_manager.update_settings(new_settings)
            self.settings = self.settings_manager.settings
            self._update_settings_display()
            self._apply_theme()
    
    def clear_log(self):
        """Clear log window"""
        self.log_window.clear()
        logging.info("Log cleared.")
    
    def cancel_analysis(self):
        """Cancel the running analysis"""
        if self.analysis_controller.is_running():
            self.analysis_controller.cancel_analysis()
            self.statusBar.showMessage("Cancelling analysis...")
    
    # Helper methods
    def _set_active_mode(self, mode):
        """Set active mode and update UI"""
        if isinstance(mode, str) or mode is None:
            mode = InteractionMode.from_string(mode)
        self.active_mode = mode
        self.toolbar_manager.set_active_mode(mode.to_string())
        
        if mode is InteractionMode.ZOOM_IN:
            self.statusBar.showMessage("Zoom in mode active - click on image to zoom in")
        elif mode is InteractionMode.ZOOM_OUT:
            self.statusBar.showMessage("Zoom out mode active - click on image to zoom out")
        elif mode is InteractionMode.SELECT:
            self.statusBar.showMessage("Selection mode active - drag to select area")
            self.visualize()
        else:
            self.statusBar.showMessage("Ready")
            self.visualize()
    
    def _mode_active(self, mode):
        """Check if a mode is currently active"""
        if isinstance(mode, str):
            mode = InteractionMode.from_string(mode)
        return self.active_mode is mode
    
    def _on_canvas_click(self, event):
        """Handle canvas click events"""
        if self.viz_controller.handle_click(event, self.active_mode):
            # Click was handled (zoom occurred)
            pass
    
    def _handle_analysis_error(self, error_msg):
        """Handle analysis errors"""
        if isinstance(error_msg, str) and error_msg.startswith('AnalysisError'):
            self.statusBar.showMessage(error_msg)
        else:
            self.statusBar.showMessage("Analysis failed")
        self.analyze_button.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.hide()
            self.statusBar.removeWidget(self.progress_bar)
    
    def _update_analysis_progress(self, message):
        """Update analysis progress"""
        self.statusBar.showMessage(message)
    
    def _handle_analysis_result(self, result_df):
        """Handle analysis results"""
        if self.data_manager.save_analysis_results(result_df):
            self._update_data_table()
            self.visualize_button.setEnabled(True)
            self.analyze_button.setEnabled(True)
            self.statusBar.showMessage("Analysis complete")
        
        # Remove progress bar
        self.progress_bar.hide()
        self.statusBar.removeWidget(self.progress_bar)
    
    def _update_data_table(self):
        """Update the data table"""
        if not self.data_manager.has_sources:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
        
        sources_df = self.data_manager.sources_df
        self.data_table.setRowCount(len(sources_df))
        self.data_table.setColumnCount(len(sources_df.columns))
        self.data_table.setHorizontalHeaderLabels(sources_df.columns)
        
        for i, row in sources_df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        self.data_table.resizeColumnsToContents()
        self.data_table.setSortingEnabled(True)
    
    def _update_settings_display(self):
        """Update settings display"""
        fits_path = self.settings['fits_file_path']
        if len(fits_path) > 50:
            fits_path = "..." + fits_path[-47:]
        
        settings_text = f"""
        FITS File: {fits_path}
        FWHM: {self.settings['analysis']['star_detection']['fwhm']}
        Threshold: {self.settings['analysis']['star_detection']['threshold_factor']}
        DPI: {self.settings['analysis']['visualization']['dpi']}
        Colormap: {self.settings['analysis']['visualization']['colormap']}
        Interpolation: {self.settings['analysis']['visualization']['interpolation']}
        """
        self.settings_label.setText(settings_text)
        self.settings_label.setWordWrap(True)
        self.settings_label.setToolTip(self.settings['fits_file_path'])
    
    def _apply_theme(self):
        """Apply the current theme"""
        if self.settings["ui"]["theme"] == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet())
        # Add other themes as needed
    
    def _apply_table_style(self):
        """Apply styling to the data table"""
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
    
    def _setup_logging(self):
        """Set up logging"""
        self.log_stream = LogStream()
        self.log_stream.newText.connect(self.log_window.append)
        
        sys.stdout = self.log_stream
        sys.stderr = self.log_stream
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=self.log_stream
        )
        
        self.log_window.append("NovaLoom started\n")
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        if self.figure is not None:
            self.figure.clear()
            self.canvas.draw()
            self.canvas.flush_events()
        
        super().resizeEvent(event)
        
        if self.data_manager.has_fits_data and self.data_manager.has_sources:
            self.resize_timer.start(100)
    
    def _handle_resize(self):
        """Handle resize completion"""
        if self.data_manager.has_fits_data and self.data_manager.has_sources:
            self.viz_controller.clear_cache()
            self.visualize()
