class NovaLoomError(Exception):
    """Base exception for NovaLoom application."""

class FitsLoadError(NovaLoomError):
    """Raised when a FITS file cannot be loaded."""

class AnalysisError(NovaLoomError):
    """Raised when analysis fails."""

class ExportError(NovaLoomError):
    """Raised when exporting data fails."""
