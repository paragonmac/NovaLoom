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
                             QProgressBar, QTableWidget, QTableWidgetItem, QApplication)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer
import qdarkstyle

from ui.widgets.log_window import LogStream, LogWindow
from core.logging_config import init_logging
from ui.widgets.settings_dialog import SettingsDialog
from ui.components.toolbar import ToolbarManager
from core.data_manager import DataManager
from core.controllers.analysis_controller import AnalysisController
from core.controllers.visualization_controller import VisualizationController
from core.settings_manager import SettingsManager
from core.enums import InteractionMode
from core.errors import FitsLoadError, ExportError, AnalysisError
from core.perf import log_timed, PerfTimer


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
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_resize)

    def _init_managers(self):
        """Initialize logging, settings, data, analysis, viz controller placeholder."""
        # Log window & logging
        self.log_window = LogWindow()
        self._setup_logging()
        # Settings
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        # Data manager
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
        self.data_manager = DataManager(results_dir)
        # Analysis controller
        self.analysis_controller = AnalysisController()
        self.analysis_controller.set_callbacks(
            on_error=self._handle_analysis_error,
            on_progress=self._update_analysis_progress,
            on_result=self._handle_analysis_result
        )

    def _setup_event_handlers(self):
        if hasattr(self, 'load_button'):
            self.load_button.clicked.connect(self.load_fits)
        if hasattr(self, 'analyze_button'):
            self.analyze_button.clicked.connect(self.analyze)
        if hasattr(self, 'visualize_button'):
            self.visualize_button.clicked.connect(self.visualize)
        # Canvas connection deferred until canvas created
        
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("NovaLoom - Astronomical Image Analysis")
        try:
            self.setMinimumSize(*self.settings["ui"]["window_size"])
        except Exception:
            self.setMinimumSize(800, 600)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Toolbar
        self.toolbar_manager = ToolbarManager(self)
        self.toolbar_manager.create_toolbar(self._get_toolbar_callbacks())

        # Splitters
        content_splitter = QSplitter(Qt.Vertical)
        top_splitter = QSplitter(Qt.Horizontal)
        left_panel = self._create_control_panel()
        right_panel = self._create_results_panel()
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setStretchFactor(1, 2)

        # Log dock
        self.log_dock = QDockWidget("Log", self)
        self.log_dock.setWidget(self.log_window)
        self.log_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        content_splitter.addWidget(top_splitter)
        layout.addWidget(content_splitter)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Menu bar (Options -> Debug)
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Options")
        from PySide6.QtGui import QAction
        self.debug_action = QAction("Enable Debug Logging", self, checkable=True)
        try:
            debug_enabled = bool(self.settings.get("debug", False))
        except Exception:
            try:
                debug_enabled = bool(self.settings["debug"])
            except Exception:
                debug_enabled = False
        self.debug_action.setChecked(debug_enabled)
        self.debug_action.triggered.connect(self._toggle_debug_logging)
        options_menu.addAction(self.debug_action)

        # Apply theme/font AFTER widgets created so stylesheet propagates
        self._apply_theme()
        self._apply_font_size()
        self._apply_debug_logging(debug_enabled)
        if not debug_enabled:
            self.log_dock.hide()
        self._apply_debug_logging(debug_enabled)
    
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
        # Only update if settings seem valid (dict-like with analysis key)
        if isinstance(self.settings, dict) and 'analysis' in self.settings:
            self._update_settings_display()
        else:
            self.settings_label.setText("Settings loading...")
        settings_layout.addWidget(self.settings_label)
        left_layout.addWidget(self.load_button)
        left_layout.addWidget(self.analyze_button)
        left_layout.addWidget(self.visualize_button)
        left_layout.addWidget(settings_group)
        left_layout.addStretch()
        return left_panel

    def _create_results_panel(self):
        right_panel = QTabWidget()
        vis_tab = QWidget()
        vis_layout = QVBoxLayout(vis_tab)
        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        vis_layout.addWidget(self.canvas)
        right_panel.addTab(vis_tab, "Visualization")
        self.viz_controller = VisualizationController(self.figure, self.canvas)
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self._apply_table_style()
        data_layout.addWidget(self.data_table)
        right_panel.addTab(data_tab, "Data")
        # Connect canvas now that it exists
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)
        return right_panel

    def _get_toolbar_callbacks(self):
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
    @log_timed("ui.load_fits")
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
    
    @log_timed("ui.analyze")
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
    
    @log_timed("ui.visualize")
    def visualize(self):
        """Update visualization"""
        success, message = self.viz_controller.visualize(
            self.data_manager, 
            self.settings, 
            active_mode=self.active_mode
        )
        self.statusBar.showMessage("Ready" if success else message)
    
    @log_timed("ui.toggle_zoom_in")
    def toggle_zoom_in(self):
        """Toggle zoom in mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.ZOOM_IN) else InteractionMode.ZOOM_IN)
    
    @log_timed("ui.toggle_zoom_out")
    def toggle_zoom_out(self):
        """Toggle zoom out mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.ZOOM_OUT) else InteractionMode.ZOOM_OUT)
    
    @log_timed("ui.toggle_selection")
    def toggle_selection(self):
        """Toggle selection mode"""
        self._set_active_mode(InteractionMode.NONE if self._mode_active(InteractionMode.SELECT) else InteractionMode.SELECT)
    
    @log_timed("ui.reset_zoom")
    def reset_zoom(self):
        """Reset zoom"""
        if self.viz_controller.reset_zoom():
            # Exit zoom modes without forcing full re-visualization
            self.active_mode = None
            self.toolbar_manager.set_active_mode(None)
            self.statusBar.showMessage("Zoom reset to full view")
    
    @log_timed("ui.reset_source_selection")
    def reset_source_selection(self):
        """Reset source selection"""
        self.data_manager.reset_selection()
        self._set_active_mode(None)
        self.visualize()
        self.statusBar.showMessage("Selection reset")
    
    @log_timed("ui.export_data")
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
    
    @log_timed("ui.show_settings")
    def show_settings(self):
        """Show settings dialog"""
        # Provide a pure Python snapshot to the dialog to avoid Lua proxy issues
        try:
            from core.settings_manager import SettingsManager as _SM
            snapshot = self.settings_manager._snapshot_lua_settings()
        except Exception:
            snapshot = self.settings if isinstance(self.settings, dict) else {}
        dialog = SettingsDialog(snapshot, self)
        if dialog.exec() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings_manager.update_settings(new_settings)
            self.settings = self.settings_manager.settings
            self._update_settings_display()
            self._apply_theme()
            self._apply_font_size()
            # Apply debug state if changed
            if 'debug' in new_settings:
                debug_enabled = bool(new_settings['debug'])
                self.debug_action.setChecked(debug_enabled)
                self._apply_debug_logging(debug_enabled)
    
    @log_timed("ui.clear_log")
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
        """Update settings display safely for Lua or dict settings."""
        if not hasattr(self, 'settings_label'):
            return
        def sget(obj, *keys, default=None):
            cur = obj
            for k in keys:
                try:
                    if isinstance(cur, dict):
                        cur = cur.get(k) if k in cur else None
                    else:
                        cur = cur[k]
                except Exception:
                    return default
            return cur if cur is not None else default
        fits_path = sget(self.settings, 'fits_file_path', default='')
        short_path = fits_path
        if isinstance(short_path, str) and len(short_path) > 50:
            short_path = '...' + short_path[-47:]
        fwhm = sget(self.settings, 'analysis','star_detection','fwhm', default='N/A')
        thresh = sget(self.settings, 'analysis','star_detection','threshold_factor', default='N/A')
        dpi = sget(self.settings, 'analysis','visualization','dpi', default='N/A')
        cmap = sget(self.settings, 'analysis','visualization','colormap', default='N/A')
        interp = sget(self.settings, 'analysis','visualization','interpolation', default='N/A')
        settings_text = (
            f"FITS File: {short_path}\n"
            f"FWHM: {fwhm}  Threshold: {thresh}\n"
            f"DPI: {dpi}  Colormap: {cmap}  Interp: {interp}"
        )
        self.settings_label.setText(settings_text)
        self.settings_label.setWordWrap(True)
        self.settings_label.setToolTip(fits_path)

    # ---- Helpers & remaining functionality reintroduced ----
    def cancel_analysis(self):
        if hasattr(self, 'analysis_controller') and self.analysis_controller.is_running():
            self.analysis_controller.cancel_analysis()
            self.statusBar.showMessage("Cancelling analysis...")

    def _set_active_mode(self, mode):
        if isinstance(mode, str) or mode is None:
            mode = InteractionMode.from_string(mode)
        self.active_mode = mode
        if hasattr(self, 'toolbar_manager'):
            self.toolbar_manager.set_active_mode(mode.to_string())
        if mode is InteractionMode.ZOOM_IN:
            self.statusBar.showMessage("Zoom in mode active - click to zoom")
        elif mode is InteractionMode.ZOOM_OUT:
            self.statusBar.showMessage("Zoom out mode active - click to zoom out")
        elif mode is InteractionMode.SELECT:
            self.statusBar.showMessage("Selection mode active")
            self.visualize()
        else:
            self.statusBar.showMessage("Ready")
            self.visualize()

    def _mode_active(self, mode):
        if isinstance(mode, str):
            mode = InteractionMode.from_string(mode)
        return getattr(self, 'active_mode', None) is mode

    def _on_canvas_click(self, event):
        if hasattr(self, 'viz_controller'):
            self.viz_controller.handle_click(event, getattr(self, 'active_mode', None))

    def _handle_analysis_error(self, error_msg):
        if isinstance(error_msg, str) and error_msg.startswith('AnalysisError'):
            self.statusBar.showMessage(error_msg)
        else:
            self.statusBar.showMessage("Analysis failed")
        if hasattr(self, 'analyze_button'):
            self.analyze_button.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.hide()
            self.statusBar.removeWidget(self.progress_bar)

    def _update_analysis_progress(self, message):
        self.statusBar.showMessage(message)

    def _handle_analysis_result(self, result_df):
        if self.data_manager.save_analysis_results(result_df):
            self._update_data_table()
            if hasattr(self, 'visualize_button'):
                self.visualize_button.setEnabled(True)
            if hasattr(self, 'analyze_button'):
                self.analyze_button.setEnabled(True)
            self.statusBar.showMessage("Analysis complete")
        if hasattr(self, 'progress_bar'):
            self.progress_bar.hide()
            self.statusBar.removeWidget(self.progress_bar)

    def _update_data_table(self):
        if not hasattr(self, 'data_table') or not self.data_manager.has_sources:
            if hasattr(self, 'data_table'):
                self.data_table.setRowCount(0)
                self.data_table.setColumnCount(0)
            return
        df = self.data_manager.sources_df
        self.data_table.setRowCount(len(df))
        self.data_table.setColumnCount(len(df.columns))
        self.data_table.setHorizontalHeaderLabels(df.columns)
        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.data_table.setItem(i, j, QTableWidgetItem(str(val)))
        self.data_table.resizeColumnsToContents()
        self.data_table.setSortingEnabled(True)

    def _apply_theme(self):
        theme = self.settings.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            self.setStyleSheet(qdarkstyle.load_stylesheet())
        elif theme == 'light':
            self.setStyleSheet("")
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet())

    def _apply_font_size(self):
        size =  int(self.settings.get('ui', {}).get('font_size', 10))
        app = QApplication.instance()
        if app:
            f = app.font() or QFont()
            f.setPointSize(size)
            app.setFont(f)

    def _apply_table_style(self):
        if hasattr(self, 'data_table'):
            self.data_table.setStyleSheet("""
                QTableWidget { background-color:#1e1e1e; color:#d4d4d4; gridline-color:#3c3c3c; alternate-background-color:#2d2d2d; }
                QHeaderView::section { background-color:#2d2d2d; color:#d4d4d4; padding:4px; border:1px solid #3c3c3c; }
            """)

    def _setup_logging(self):
        self.log_stream = LogStream()
        self.log_stream.newText.connect(lambda text: self.log_window.append(text))
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        init_logging(level=logging.INFO)
        root_logger = logging.getLogger()
        if not any(getattr(h, 'name', '') == 'QtLogHandler' for h in root_logger.handlers):
            class QtLogHandler(logging.Handler):
                def __init__(self, stream):
                    super().__init__()
                    self.stream = stream
                    self.name = 'QtLogHandler'
                def emit(self, record):
                    try:
                        msg = self.format(record)
                        if not msg.endswith('\n'):
                            msg += '\n'
                        self.stream.write(msg)
                    except Exception:
                        self.handleError(record)
            h = QtLogHandler(self.log_stream)
            h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))
            root_logger.addHandler(h)
        self.log_window.append('NovaLoom started\n')

    def _apply_debug_logging(self, enabled: bool):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG if enabled else logging.INFO)
        for h in root.handlers:
            if getattr(h, 'name', '') == 'QtLogHandler':
                h.setLevel(logging.DEBUG if enabled else logging.INFO)
        if enabled:
            if sys.stdout is not self.log_stream:
                sys.stdout = self.log_stream
            if sys.stderr is not self.log_stream:
                sys.stderr = self.log_stream
            logging.getLogger(__name__).info('Debug logging enabled')
        else:
            if sys.stdout is self.log_stream:
                sys.stdout = self._orig_stdout
            if sys.stderr is self.log_stream:
                sys.stderr = self._orig_stderr
            logging.getLogger(__name__).info('Debug logging disabled')
        if hasattr(self, 'log_dock'):
            self.log_dock.setVisible(enabled)

    def _toggle_debug_logging(self, checked: bool):
        try:
            window_size = list(self.settings['ui']['window_size'])
        except Exception:
            window_size = [800, 600]
        new_settings = {
            'fits_file_path': self.settings.get('fits_file_path', ''),
            'analysis': {
                'star_detection': dict(self.settings['analysis']['star_detection']),
                'visualization': dict(self.settings['analysis']['visualization']),
            },
            'ui': { **dict(self.settings['ui']), 'window_size': window_size },
            'debug': bool(checked)
        }
        self.settings_manager.update_settings(new_settings)
        self.settings = self.settings_manager.settings
        self._apply_debug_logging(bool(checked))

    def resizeEvent(self, event):
        if hasattr(self, 'figure') and self.figure is not None:
            self.figure.clear()
            self.canvas.draw()
            self.canvas.flush_events()
        super().resizeEvent(event)
        if self.data_manager.has_fits_data and self.data_manager.has_sources:
            if hasattr(self, 'resize_timer'):
                self.resize_timer.start(100)

    def _handle_resize(self):
        if self.data_manager.has_fits_data and self.data_manager.has_sources:
            if hasattr(self, 'viz_controller'):
                self.viz_controller.clear_cache()
            self.visualize()
    
    def _apply_theme(self):
        """Apply the current theme"""
        theme = None
        try:
            theme = self.settings["ui"]["theme"]
        except Exception:
            theme = "dark"

        if theme == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet())
        elif theme == "light":
            # Clear styles for native light look
            self.setStyleSheet("")
        else:
            # Unknown theme -> fallback to dark
            self.setStyleSheet(qdarkstyle.load_stylesheet())

    def _apply_font_size(self):
        """Apply global font size from settings."""
        try:
            size = int(self.settings['ui']['font_size'])
        except Exception:
            size = 10
        app = QApplication.instance()
        if app:
            font = app.font() if app.font() else QFont()
            if font.pointSize() != size:
                font.setPointSize(size)
                app.setFont(font)
    
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
        # Stream for stdout/stderr redirection and direct logging handler emission
        self.log_stream = LogStream()
        self.log_stream.newText.connect(self.log_window.append)

        # Preserve originals for restoration of prints
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr

        # Initialize standard logging (file + console) if not already
        init_logging(level=logging.INFO)
        root_logger = logging.getLogger()

        # Attach a Qt log handler to pipe log records into the log window
        if not any(getattr(h, "name", "") == "QtLogHandler" for h in root_logger.handlers):
            class QtLogHandler(logging.Handler):
                def __init__(self, stream):
                    super().__init__()
                    self.stream = stream
                    self.name = "QtLogHandler"
                def emit(self, record):
                    try:
                        msg = self.format(record)
                        # Ensure newline separation like standard handlers
                        if not msg.endswith("\n"):
                            msg += "\n"
                        self.stream.write(msg)
                    except Exception:
                        self.handleError(record)
            qt_handler = QtLogHandler(self.log_stream)
            qt_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))
            root_logger.addHandler(qt_handler)

        self.log_window.append("NovaLoom started\n")

    def _apply_debug_logging(self, enabled: bool):
        """Enable or disable debug logging and stdout capture."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG if enabled else logging.INFO)

        # Adjust Qt handler level if present
        for h in root_logger.handlers:
            if getattr(h, 'name', '') == 'QtLogHandler':
                h.setLevel(logging.DEBUG if enabled else logging.INFO)

        # Redirect stdout/stderr only when debug enabled to capture prints
        if enabled:
            if sys.stdout is not self.log_stream:
                sys.stdout = self.log_stream
            if sys.stderr is not self.log_stream:
                sys.stderr = self.log_stream
            logging.getLogger(__name__).info("Debug logging enabled")
        else:
            # Restore originals
            if hasattr(self, '_orig_stdout') and self._orig_stdout and sys.stdout is self.log_stream:
                sys.stdout = self._orig_stdout
            if hasattr(self, '_orig_stderr') and self._orig_stderr and sys.stderr is self.log_stream:
                sys.stderr = self._orig_stderr
            logging.getLogger(__name__).info("Debug logging disabled")
        # Show/hide log dock when not debugging (still allow manual reopen if wanted)
        if hasattr(self, 'log_dock'):
            self.log_dock.setVisible(True if enabled else False)

    def _toggle_debug_logging(self, checked: bool):
        """Menu action to toggle debug logging."""
        # Update settings and apply
        try:
            # Settings may be Lua table proxy; update via manager
            current = dict(self.settings)
        except Exception:
            current = { 'debug': bool(checked) }
        # Build a Python dict representation for update
        # Capture existing window_size if available so we don't drop it
        try:
            window_size = list(self.settings['ui']['window_size'])
        except Exception:
            window_size = [800, 600]
        new_settings = {
            'fits_file_path': self.settings['fits_file_path'],
            'analysis': {
                'star_detection': dict(self.settings['analysis']['star_detection']),
                'visualization': dict(self.settings['analysis']['visualization'])
            },
            'ui': { **dict(self.settings['ui']), 'window_size': window_size },
            'debug': bool(checked)
        }
        self.settings_manager.update_settings(new_settings)
        self.settings = self.settings_manager.settings
        self._apply_debug_logging(bool(checked))
    
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
