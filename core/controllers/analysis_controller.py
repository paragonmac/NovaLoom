"""
Analysis controller for managing background analysis operations.
"""
import logging
from PySide6.QtCore import QThread
from core.workers import AnalysisWorker


class AnalysisController:
    """Manages analysis operations and threading"""
    
    def __init__(self):
        self.analysis_thread = None
        self.analysis_worker = None
        self.callbacks = {}
    
    def set_callbacks(self, on_error=None, on_progress=None, on_result=None):
        """Set callback functions for analysis events"""
        self.callbacks = {
            'error': on_error,
            'progress': on_progress,
            'result': on_result
        }
    
    def start_analysis(self, data_manager, settings):
        """Start background analysis"""
        if not data_manager.has_fits_data:
            logging.error("No FITS data loaded")
            return False, "No FITS data loaded"
        
        if self.analysis_thread is not None and self.analysis_thread.isRunning():
            logging.warning("Analysis already in progress")
            return False, "Analysis already in progress"
        
        logging.info("Starting analysis...")
        
        # Get analysis settings
        fwhm = settings["analysis"]["star_detection"]["fwhm"]
        threshold = settings["analysis"]["star_detection"]["threshold_factor"]
        
        # Create worker and thread
        self.analysis_worker = AnalysisWorker(data_manager.fits_data, fwhm, threshold)
        self.analysis_thread = QThread()
        
        # Move worker to thread
        self.analysis_worker.moveToThread(self.analysis_thread)
        
        # Connect signals
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        
        # Connect callbacks
        if self.callbacks.get('error'):
            self.analysis_worker.error.connect(self.callbacks['error'])
        if self.callbacks.get('progress'):
            self.analysis_worker.progress.connect(self.callbacks['progress'])
        if self.callbacks.get('result'):
            self.analysis_worker.result.connect(self.callbacks['result'])
        
        # Start the thread
        self.analysis_thread.start()
        return True, "Analysis started"
    
    def is_running(self):
        """Check if analysis is currently running"""
        return self.analysis_thread is not None and self.analysis_thread.isRunning()
    
    def cleanup(self):
        """Clean up resources"""
        if self.analysis_thread is not None:
            if self.analysis_thread.isRunning():
                self.analysis_thread.quit()
                self.analysis_thread.wait()
            self.analysis_thread = None
        self.analysis_worker = None
