#!/usr/bin/env python
"""CLI: Load and display FITS file information using Lua settings + overrides.

Usage examples:
  python -m astro_analysis.scripts.load_fits
  python -m astro_analysis.scripts.load_fits --fits Data/Light_M42_180.0s_Bin1_0016.fit
  python -m astro_analysis.scripts.load_fits --fwhm 4.0 --threshold-factor 6
"""
from __future__ import annotations
import numpy as np
from ._cli_common import build_arg_parser, init_logging, load_settings, get_fits


def main():
    parser = build_arg_parser("Load a FITS file and display structural info")
    args = parser.parse_args()
    init_logging(args.debug)
    sm = load_settings(args)
    try:
        data, header, wcs = get_fits(sm.settings)
    except Exception as e:
        print(f"Error loading FITS file: {e}")
        return 1

    print(f"Loaded FITS file: {sm.settings.get('fits_file_path')}")
    print("Image Data Shape:", data.shape)
    print("Image Data Type:", data.dtype)
    print("Image Data Range:", np.nanmin(data), "to", np.nanmax(data))
    print("\nFITS Header (truncated):")
    for key in list(header.keys())[:40]:
        if key not in ("COMMENT", "HISTORY"):
            print(f"  {key}: {header[key]}")
    print("\nWCS Celestial:", wcs)
    print("\nSample (5x5):\n", data[0:5, 0:5])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())