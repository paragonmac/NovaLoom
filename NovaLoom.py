import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

os.environ['QT_API'] = 'pyside6'  # Force PySide6

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="qdarkstyle")

from PySide6.QtWidgets import QApplication
import ui.resources_rc  # Ensure Qt resources are registered
from ui.main_window import AstroAnalysisUI
from core.logging_config import init_logging, get_logger


if __name__ == "__main__":
    init_logging()
    log = get_logger(__name__)
    app = QApplication([])
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = AstroAnalysisUI()
    window.show()
    log.info("Application started")
    app.exec()
