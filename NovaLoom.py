import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

os.environ['QT_API'] = 'pyside6'  # Force PySide6

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="qdarkstyle")

from PySide6.QtWidgets import QApplication
from ui.main_window import AstroAnalysisUI


if __name__ == "__main__":
    app = QApplication([])
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = AstroAnalysisUI()
    window.show()
    app.exec()
