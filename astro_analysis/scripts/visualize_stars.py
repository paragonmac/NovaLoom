#!/usr/bin/env python
"""CLI: Visualize detected stars using sources CSV & current Lua settings."""
from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt
from ._cli_common import build_arg_parser, init_logging, load_settings, get_fits
from astro_analysis.visualization.plotting import plot_image_with_labels  # type: ignore

def visualize_stars(sm):
    """Load data and create visualization of detected stars."""
    fits_path = sm.settings.get('fits_file_path', '')
    print(f"Loading FITS file: {fits_path}")
    data, header, wcs = get_fits(sm.settings)

    csv_path = "detected_stars.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run detect_stars.py first.")
        return
    print(f"Loading detected stars from {csv_path}")
    sources_df = pd.read_csv(csv_path)

    print("\nCreating visualization...")
    fig = plot_image_with_labels(
        data=data,
        sources_df=sources_df,
        wcs=wcs,
        header=header,
        fits_file_path=fits_path
    )
    output_path = "annotated_stars.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved visualization to {output_path}")
    plt.show()

def main():
    parser = build_arg_parser("Visualize previously detected stars")
    args = parser.parse_args()
    init_logging(args.debug)
    sm = load_settings(args)
    try:
        visualize_stars(sm)
    except Exception as e:
        print(f"Visualization error: {e}")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys as _sys
    _sys.exit(main())