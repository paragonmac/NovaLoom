import warnings

def configure_warnings():
    """Configure warning filters for the application."""
    warnings.filterwarnings('ignore', category=UserWarning, append=True)
    warnings.filterwarnings('ignore', category=FutureWarning, append=True)
    warnings.filterwarnings("ignore", message="invalid value encountered", category=RuntimeWarning) 