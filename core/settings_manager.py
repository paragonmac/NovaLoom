"""
Settings management for NovaLoom application.
"""
import os
import logging
import lupa


class SettingsManager:
    """Manages application settings using Lua configuration"""
    
    def __init__(self):
        self.lua = lupa.LuaRuntime()
        self.settings = None
        self._init_lua_settings()
    
    def _init_lua_settings(self):
        """Initialize the Lua settings table"""
        try:
            # Create the settings table in Lua
            self.lua.execute("""
                settings = {
                    fits_file_path = "",
                    analysis = {
                        star_detection = {
                            fwhm = 2.5,
                            threshold_factor = 5.0
                        },
                        visualization = {
                            dpi = 100,
                            colormap = "viridis",
                            max_sources_display = 100,
                            interpolation = "bilinear"
                        }
                    },
                    ui = {
                        theme = "dark",
                        font_size = 10,
                        window_size = {800, 600}
                    }
                }
            """)
            
            # Load settings from file if it exists
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.lua")
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r") as f:
                        self.lua.execute(f.read())
                except Exception as e:
                    logging.warning(f"Could not load settings file: {str(e)}")
            
            # Get the settings table
            self.settings = self.lua.execute("settings")
            
        except Exception as e:
            logging.error(f"Error initializing settings: {str(e)}")
            # Create a Python dictionary as fallback
            self.settings = {
                "fits_file_path": "",
                "analysis": {
                    "star_detection": {
                        "fwhm": 2.5,
                        "threshold_factor": 5.0
                    },
                    "visualization": {
                        "dpi": 100,
                        "colormap": "viridis",
                        "max_sources_display": 100,
                        "interpolation": "bilinear"
                    }
                },
                "ui": {
                    "theme": "dark",
                    "font_size": 10,
                    "window_size": [800, 600]
                }
            }
    
    def update_settings(self, new_settings):
        """Update settings and save to file"""
        try:
            # Update settings in Lua
            for key, value in new_settings.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict):
                            for subsubkey, subsubvalue in subvalue.items():
                                if isinstance(subsubvalue, str):
                                    self.lua.execute(f"settings['{key}']['{subkey}']['{subsubkey}'] = '{subsubvalue}'")
                                else:
                                    self.lua.execute(f"settings['{key}']['{subkey}']['{subsubkey}'] = {subsubvalue}")
                        else:
                            if isinstance(subvalue, str):
                                self.lua.execute(f"settings['{key}']['{subkey}'] = '{subvalue}'")
                            else:
                                self.lua.execute(f"settings['{key}']['{subkey}'] = {subvalue}")
                else:
                    if isinstance(value, str):
                        self.lua.execute(f"settings['{key}'] = '{value}'")
                    else:
                        self.lua.execute(f"settings['{key}'] = {value}")
            
            # Save settings to file
            self.save_settings(new_settings)
            
            # Reload settings from Lua
            self.settings = self.lua.execute("settings")
            
        except Exception as e:
            logging.error(f"Error updating settings: {str(e)}")
            # Update Python settings as fallback
            self.settings = new_settings
    
    def save_settings(self, settings):
        """Save settings to Lua file"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.lua")
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        
        with open(settings_path, "w") as f:
            f.write("settings = {\n")
            for key, value in settings.items():
                if isinstance(value, dict):
                    f.write(f"    {key} = {{\n")
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict):
                            f.write(f"        {subkey} = {{\n")
                            for subsubkey, subsubvalue in subvalue.items():
                                if isinstance(subsubvalue, str):
                                    f.write(f"            {subsubkey} = '{subsubvalue}',\n")
                                else:
                                    f.write(f"            {subsubkey} = {subsubvalue},\n")
                            f.write("        },\n")
                        else:
                            if isinstance(subvalue, str):
                                f.write(f"        {subkey} = '{subvalue}',\n")
                            else:
                                f.write(f"        {subkey} = {subvalue},\n")
                    f.write("    },\n")
                else:
                    if isinstance(value, str):
                        f.write(f"    {key} = '{value}',\n")
                    else:
                        f.write(f"    {key} = {value},\n")
            f.write("}\n")
