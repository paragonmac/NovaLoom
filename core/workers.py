"""
Worker classes for background processing in NovaLoom.
"""
from PySide6.QtCore import QObject, Signal, Slot
from astro_analysis.data_processing.star_detection import detect_sources


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
