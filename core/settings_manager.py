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
            init_code = (
                "settings = {"\
                "\n  fits_file_path = '',"\
                "\n  analysis = {"\
                "\n    star_detection = { fwhm = 2.5, threshold_factor = 5.0 },"\
                "\n    visualization = { dpi = 100, colormap = 'viridis', max_sources_display = 100, interpolation = 'bilinear' }"\
                "\n  },"\
                "\n  ui = { theme = 'dark', font_size = 10, window_size = {800, 600} },"\
                "\n  debug = false"\
                "\n}"
            )
            try:
                self.lua.execute(init_code)
            except Exception as e:
                logging.error(f"Lua init default table failed: {e}")
                raise
            
            # Load settings from file if it exists
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.lua")
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    try:
                        self.lua.execute(file_content)
                    except Exception as le:
                        preview = file_content[:200].replace('\n', '\\n')
                        logging.warning(f"Could not load settings file: {le} | preview: {preview}")
                except Exception as e:
                    logging.warning(f"Failed reading settings file: {e}")
            
            # Get the settings table (must use eval to fetch variable value)
            try:
                self.settings = self.lua.eval('settings')
            except Exception as e:
                logging.error(f"Failed to evaluate settings table: {e}")
                raise
            
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
                    },
                    "debug": False
            }
    
    def update_settings(self, new_settings):
        """Update settings and save to file"""
        try:
            # Instead of incremental per-field executes (prone to syntax issues), build a full merged dict then overwrite
            current = self._snapshot_lua_settings()
            def merge(dst, src):
                for k, v in src.items():
                    if isinstance(v, dict) and isinstance(dst.get(k), dict):
                        merge(dst[k], v)
                    else:
                        dst[k] = v
                return dst
            merged = merge(current if isinstance(current, dict) else {}, new_settings)
            self.save_settings(merged)
            # Reload into Lua fresh
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.lua"), 'r', encoding='utf-8') as f:
                self.lua.execute(f.read())
            self.settings = self.lua.eval('settings')
            
            # Reload settings from Lua
            try:
                self.settings = self.lua.eval('settings')
            except Exception as e:
                logging.error(f"Failed to evaluate settings after update: {e}")
                raise
            
        except Exception as e:
            logging.error(f"Error updating settings: {str(e)}")
            # Update Python settings as fallback
            self.settings = new_settings

    def _snapshot_lua_settings(self):
        """Create a full Python representation of the current Lua settings table.

        Preserves lists (numeric consecutive keys starting at 1) as Python lists
        and other tables as dictionaries. This ensures we don't lose keys that
        weren't part of a partial update (e.g. window_size).
        """
        try:
            settings_table = self.lua.eval('settings')  # get table reference

            def convert(value):
                # Detect nested table (Lua table proxies expose .keys())
                if hasattr(value, 'keys'):
                    keys = list(value.keys())
                    # Determine if table is an array: all integer, contiguous starting at 1
                    int_keys = [k for k in keys if isinstance(k, (int, float)) and int(k) == k]
                    if len(int_keys) == len(keys):
                        max_index = int(max(int_keys)) if int_keys else 0
                        if set(int(k) for k in int_keys) == set(range(1, max_index + 1)):
                            # Treat as list (1-based in Lua)
                            return [convert(value[i]) for i in range(1, max_index + 1)]
                    # Fallback: treat as dict
                    result = {}
                    for k in keys:
                        result[k] = convert(value[k])
                    return result
                # Primitive
                return value

            return convert(settings_table)
        except Exception as e:
            logging.warning(f"Failed to snapshot Lua settings, using current Python copy: {e}")
            return self.settings
    
    def save_settings(self, settings):
        """Save settings to Lua file"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.lua")
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        def to_lua(value):
            if isinstance(value, bool):
                return 'true' if value else 'false'
            if isinstance(value, (int, float)):
                return str(value)
            if isinstance(value, str):
                return f"'{value.replace("'", "\\'")}'"
            if isinstance(value, (list, tuple)):
                return '{ ' + ', '.join(to_lua(v) for v in value) + ' }'
            return str(value)

        def write_table(f, table, indent=0):
            pad = ' ' * indent
            f.write(pad + '{\n')
            items = list(table.items())
            for idx, (k, v) in enumerate(items):
                is_last = idx == len(items) - 1
                f.write(pad + '  ' + f"{k} = ")
                if isinstance(v, dict):
                    write_table(f, v, indent + 2)
                else:
                    f.write(to_lua(v))
                f.write(',\n' if not is_last else '\n')
            f.write(pad + '}')

        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write('settings = ')
            write_table(f, settings, 0)
            f.write('\n')

        # Verification: attempt to load file content with a separate Lua state to catch syntax early
        try:
            verify_lua = lupa.LuaRuntime()
            with open(settings_path, 'r', encoding='utf-8') as vf:
                verify_lua.execute(vf.read())
        except Exception as e:
            logging.error(f"Wrote invalid Lua settings file: {e}")
