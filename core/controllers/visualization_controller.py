"""
Visualization controller for managing plot display and interactions.
"""
import logging
from matplotlib.widgets import RectangleSelector
from astro_analysis.visualization.plotting import plot_image_with_labels


class VisualizationController:
    """Manages visualization display and user interactions"""
    
    def __init__(self, figure, canvas):
        self.figure = figure
        self.canvas = canvas
        self.original_limits = None
        self.rect_selector = None
        
        # Visualization state
        self.visualization_in_progress = False
        self.plot_cache = {
            'data': None,
            'sources': None,
            'cmap': None,
            'interpolation': None,
            'show_labels': None
        }
        
        # Zoom state
        self.zoom_level = 1.0
        self.zoom_center = None
    
    def visualize(self, data_manager, settings, force_redraw=False, active_mode=None):
        """Update the visualization with current data"""
        if not data_manager.has_fits_data or not data_manager.has_sources:
            logging.warning("Cannot visualize: FITS data or source data missing")
            return False, "Data missing for visualization"
        
        if self.visualization_in_progress:
            return False, "Visualization in progress"
        
        self.visualization_in_progress = True
        logging.info("Updating visualization...")
        
        try:
            # Get visualization settings
            cmap = settings["analysis"]["visualization"]["colormap"]
            max_sources = settings["analysis"]["visualization"]["max_sources_display"]
            interpolation = settings["analysis"]["visualization"]["interpolation"]
            
            # Get sources to display
            display_df = data_manager.get_display_sources(max_sources)
            
            # Show labels if we have selected sources or are in selection mode
            show_labels = data_manager.has_selection or active_mode == 'select'
            
            # Check if we need to redraw
            needs_redraw = force_redraw or (
                self.plot_cache['data'] is None or
                self.plot_cache['sources'] is not display_df or
                self.plot_cache['cmap'] != cmap or
                self.plot_cache['interpolation'] != interpolation or
                self.plot_cache['show_labels'] != show_labels
            )
            
            if needs_redraw:
                # Clear the figure
                self.figure.clear()
                
                # Create plot
                plot_image_with_labels(
                    data=data_manager.fits_data,
                    sources_df=display_df,
                    wcs=data_manager.fits_wcs,
                    header=data_manager.fits_header,
                    fits_file_path=settings["fits_file_path"],
                    cmap=cmap,
                    fig=self.figure,
                    interpolation=interpolation,
                    show_labels=show_labels
                )
                
                # Store original limits for reset
                ax = self.figure.gca()
                self.original_limits = (ax.get_xlim(), ax.get_ylim())
                
                # Add rectangle selector if in selection mode
                if active_mode == 'select':
                    self.rect_selector = RectangleSelector(
                        self.figure.gca(),
                        lambda eclick, erelease: self._handle_selection(eclick, erelease, data_manager),
                        useblit=True,
                        button=[1],  # Left mouse button
                        minspanx=5, minspany=5,  # Minimum size
                        spancoords='data',
                        interactive=True
                    )
                
                # Update cache
                self.plot_cache = {
                    'data': data_manager.fits_data,
                    'sources': display_df,
                    'cmap': cmap,
                    'interpolation': interpolation,
                    'show_labels': show_labels
                }
            
            # Update canvas
            self.canvas.draw()
            logging.info("Visualization updated")
            return True, "Visualization updated"
            
        except Exception as e:
            logging.error(f"Error during visualization: {str(e)}")
            return False, f"Visualization failed: {str(e)}"
        finally:
            self.visualization_in_progress = False
    
    def handle_click(self, event, active_mode):
        """Handle mouse clicks for zooming"""
        if event.inaxes is None or active_mode is None:
            return False
        
        if active_mode == 'zoom_in':
            self.zoom_center = (event.xdata, event.ydata)
            self.zoom_level = 2.0  # Fixed 2x zoom
            self._update_zoom()
            logging.info("Zoomed in 2x")
            return True
        elif active_mode == 'zoom_out':
            self.zoom_center = (event.xdata, event.ydata)
            self.zoom_level = 0.5  # Fixed 0.5x zoom (2x out)
            self._update_zoom()
            logging.info("Zoomed out 2x")
            return True
        
        return False
    
    def reset_zoom(self):
        """Reset zoom to show entire image"""
        self.zoom_level = 1.0
        self.zoom_center = None
        
        if self.original_limits is not None:
            ax = self.figure.gca()
            ax.set_xlim(self.original_limits[0])
            ax.set_ylim(self.original_limits[1])
            self.canvas.draw()
            logging.info("Zoom reset to full view")
            return True
        return False
    
    def clear_cache(self):
        """Clear the plot cache to force redraw"""
        self.plot_cache = {
            'data': None,
            'sources': None,
            'cmap': None,
            'interpolation': None,
            'show_labels': None
        }
    
    def _update_zoom(self):
        """Update the plot with current zoom level"""
        ax = self.figure.gca()
        
        # Get current axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Calculate new limits based on zoom level and center
        if self.zoom_center is not None:
            x_center, y_center = self.zoom_center
            x_range = (xlim[1] - xlim[0]) / self.zoom_level
            y_range = (ylim[1] - ylim[0]) / self.zoom_level
            
            new_xlim = (x_center - x_range/2, x_center + x_range/2)
            new_ylim = (y_center - y_range/2, y_center + y_range/2)
        else:
            # If no center point, zoom around the center of the current view
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) / self.zoom_level
            y_range = (ylim[1] - ylim[0]) / self.zoom_level
            
            new_xlim = (x_center - x_range/2, x_center + x_range/2)
            new_ylim = (y_center - y_range/2, y_center + y_range/2)
        
        # Set new limits
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        
        # Redraw the canvas
        self.canvas.draw()
    
    def _handle_selection(self, eclick, erelease, data_manager):
        """Handle rectangle selection"""
        # Get selection coordinates
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Ensure coordinates are in the correct order
        xmin, xmax = min(x1, x2), max(x1, x2)
        ymin, ymax = min(y1, y2), max(y1, y2)
        
        # Use data manager to select sources
        num_selected = data_manager.select_sources_in_region(xmin, xmax, ymin, ymax)
        return num_selected
