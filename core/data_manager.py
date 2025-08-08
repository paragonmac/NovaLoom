"""
Data manager for handling FITS data and analysis results.
"""
import os
import logging
import pandas as pd
from astro_analysis.utils.io import read_fits
from core.errors import FitsLoadError, ExportError


class DataManager:
    """Manages FITS data, analysis results, and file operations"""
    
    def __init__(self, results_dir):
        self.results_dir = results_dir
        self.fits_data = None
        self.fits_header = None
        self.fits_wcs = None
        self.sources_df = None
        self.selected_sources_df = None
        self.current_fits_path = None
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_fits_file(self, file_path):
        """Load a FITS file and return success status"""
        try:
            self.current_fits_path = file_path
            self.fits_data, self.fits_header, self.fits_wcs = read_fits(file_path)
            logging.info("FITS file loaded successfully")
            
            # Check for cached results
            results_path = self._get_results_path(file_path)
            if os.path.exists(results_path):
                logging.info(f"Loading cached results from {results_path}")
                self.sources_df = pd.read_csv(results_path)
                return True, "loaded_with_cache"
            
            # Clear previous analysis if no cache
            self.sources_df = None
            self.selected_sources_df = None
            return True, "loaded_no_cache"
            
        except Exception as e:
            logging.error(f"Error loading FITS file: {str(e)}")
            raise FitsLoadError(str(e))
    
    def save_analysis_results(self, results_df):
        """Save analysis results to CSV"""
        try:
            self.sources_df = results_df
            results_path = self._get_results_path(self.current_fits_path)
            self.sources_df.to_csv(results_path, index=False)
            logging.info(f"Saved analysis results to {results_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")
            return False
    
    def export_data(self, file_path):
        """Export current data to CSV file"""
        if self.sources_df is None:
            raise ExportError("No data to export")
        
        try:
            self.sources_df.to_csv(file_path, index=False)
            logging.info(f"Data exported to {file_path}")
            return True, f"Data exported to {file_path}"
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            raise ExportError(str(e))
    
    def select_sources_in_region(self, xmin, xmax, ymin, ymax):
        """Select sources within a rectangular region"""
        if self.sources_df is None:
            return 0
        
        mask = (
            (self.sources_df['xcentroid'] >= xmin) &
            (self.sources_df['xcentroid'] <= xmax) &
            (self.sources_df['ycentroid'] >= ymin) &
            (self.sources_df['ycentroid'] <= ymax)
        )
        
        self.selected_sources_df = self.sources_df[mask]
        num_selected = len(self.selected_sources_df)
        total_sources = len(self.sources_df)
        
        logging.info(f"Selected {num_selected} of {total_sources} sources")
        return num_selected
    
    def reset_selection(self):
        """Reset source selection"""
        self.selected_sources_df = None
        logging.info("Source selection reset")
    
    def get_display_sources(self, max_sources):
        """Get sources for display, respecting limits"""
        display_df = self.selected_sources_df if self.selected_sources_df is not None else self.sources_df
        
        if display_df is None:
            return None
        
        if len(display_df) > max_sources:
            display_df = display_df.head(max_sources)
            logging.info(f"Displaying {max_sources} of {len(display_df)} sources")
        
        return display_df
    
    def _get_results_path(self, fits_path):
        """Get the path for cached results based on the FITS file path"""
        filename = os.path.basename(fits_path)
        base_name = os.path.splitext(filename)[0]
        return os.path.join(self.results_dir, f"{base_name}_sources.csv")
    
    @property
    def has_fits_data(self):
        """Check if FITS data is loaded"""
        return self.fits_data is not None
    
    @property
    def has_sources(self):
        """Check if analysis results are available"""
        return self.sources_df is not None
    
    @property
    def has_selection(self):
        """Check if sources are selected"""
        return self.selected_sources_df is not None
