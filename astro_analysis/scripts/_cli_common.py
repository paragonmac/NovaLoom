"""Common helpers for CLI scripts using the Lua settings manager.

Allows the legacy script entry points to pull configuration from
`config/settings.lua` while providing lightweight command-line overrides.
"""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
from astropy.wcs import WCS

# Project root = two levels up from this file (astro_analysis/scripts)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Import SettingsManager and FITS loader
# (Importing via absolute package name so scripts can be executed as modules.)
from core.settings_manager import SettingsManager  # type: ignore
from astro_analysis.data_processing.fits_loader import load_fits_file  # type: ignore

log = logging.getLogger("cli")


def build_arg_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--fits", dest="fits_file_path", help="Override FITS file path from settings.lua")
    p.add_argument("--fwhm", type=float, help="Override star detection FWHM (pixels)")
    p.add_argument("--threshold-factor", type=float, help="Override star detection threshold factor")
    p.add_argument("--no-save", action="store_true", help="Do not persist overrides back to settings.lua")
    p.add_argument("--debug", action="store_true", help="Enable debug logging for this run only")
    return p


def init_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def load_settings(args) -> SettingsManager:
    sm = SettingsManager()
    settings = sm.settings
    modified = False
    # Apply overrides (in-memory first)
    if args.fits_file_path:
        settings["fits_file_path"] = args.fits_file_path
        modified = True
    if args.fwhm is not None:
        settings["analysis"]["star_detection"]["fwhm"] = float(args.fwhm)
        modified = True
    if args.threshold_factor is not None:
        settings["analysis"]["star_detection"]["threshold_factor"] = float(args.threshold_factor)
        modified = True
    # Persist if user did not opt out
    if modified and not args.no_save:
        sm.update_settings(settings)
    return sm


def get_fits(settings) -> Tuple[np.ndarray, any, WCS]:  # header type is fits.header.Header but keep generic
    fits_path = settings.get("fits_file_path") or ""
    if not fits_path:
        raise FileNotFoundError("No fits_file_path set in settings (config/settings.lua)")
    return load_fits_file(fits_path)
