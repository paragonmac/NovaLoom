"""Worker classes for background processing in NovaLoom.

Enhancements:
 - Adds background estimation prior to source detection
 - Interprets provided threshold value as a threshold *factor* (multiplied by
     measured noise) rather than an absolute value
 - Provides cooperative cancellation support
 - Ensures finished signal is emitted on both success and error paths so the
     controller thread is always cleaned up.
"""
from PySide6.QtCore import QObject, Signal, Slot
from astro_analysis.data_processing.star_detection import (
        detect_sources,
        estimate_background,
)
from core.errors import AnalysisError
from core.perf import time_block
import logging

logger = logging.getLogger(__name__)


class AnalysisWorker(QObject):
    """Worker class for running analysis in a separate thread.

    Parameters
    ----------
    data : ndarray
        FITS image data.
    fwhm : float
        Expected FWHM in pixels for stellar PSF.
    threshold_factor : float
        Multiplicative factor applied to the estimated background noise to
        derive the absolute detection threshold.
    """
    finished = Signal()          # Emitted when analysis is complete (success or error)
    error = Signal(str)          # Emitted when an error occurs
    progress = Signal(str)       # Progress message updates
    result = Signal(object)      # Emitted with pandas DataFrame of detected sources

    def __init__(self, data, fwhm, threshold_factor):
        super().__init__()
        self.data = data
        self.fwhm = fwhm
        self.threshold_factor = threshold_factor
        self._cancelled = False

    def cancel(self):
        """Request cooperative cancellation."""
        self._cancelled = True

    def _check_cancelled(self):
        if self._cancelled:
            raise RuntimeError("Analysis cancelled by user")

    @Slot()
    def run(self):
        """Run the analysis with background estimation and cooperative cancellation."""
        try:
            with time_block("analysis.total"):
                self.progress.emit("Estimating background...")
                self._check_cancelled()
                with time_block("analysis.background"):
                    bg_subtracted, noise_std = estimate_background(
                        self.data,
                        box_size=(64, 64),
                        filter_size=(3, 3),
                    )
                self.progress.emit(f"Background estimated (noise σ≈{noise_std:.2f})")
                self._check_cancelled()
                abs_threshold = noise_std * self.threshold_factor
                self.progress.emit(
                    f"Detecting sources (FWHM={self.fwhm}, threshold={abs_threshold:.2f})..."
                )
                with time_block("analysis.detect"):
                    sources_table = detect_sources(
                        bg_subtracted,
                        fwhm=self.fwhm,
                        threshold=abs_threshold,
                    )
                self._check_cancelled()
                self.progress.emit("Converting results...")
                with time_block("analysis.convert"):
                    result_df = sources_table.to_pandas()
                self.result.emit(result_df)
        except RuntimeError as e:
            # Cooperative cancellation path
            logger.info("Analysis cancelled by user")
            self.error.emit(str(e))
        except Exception as e:
            # Wrap unexpected errors in AnalysisError for uniform UI messaging
            logger.exception("Analysis worker error")
            self.error.emit(str(AnalysisError(str(e))))
        finally:
            # Always emit finished so thread can be cleaned up
            self.finished.emit()


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
