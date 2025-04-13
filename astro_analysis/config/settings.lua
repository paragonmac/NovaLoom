-- NovaLoom Configuration Settings

-- File paths
local settings = {
    -- Default FITS file path
    fits_file_path = "Data/Light_M42_180.0s_Bin1_0016.fit",
    
    -- Output paths
    output = {
        stars_csv = "detected_stars.csv",
        visualization = "annotated_stars.png",
        reports = "analysis_report.txt"
    },
    
    -- Analysis settings
    analysis = {
        -- Star detection
        star_detection = {
            fwhm = 3.0,
            threshold_factor = 5.0,
            box_size = {50, 50},
            filter_size = {3, 3}
        },
        
        -- Visualization
        visualization = {
            dpi = 300,
            colormap = "viridis",
            show_labels = true,
            label_size = 10,
            marker_size = 5
        },
        
        -- Coordinate system
        coordinates = {
            system = "icrs",  -- ICRS, Galactic, etc.
            epoch = "J2000"
        }
    },
    
    -- UI settings
    ui = {
        theme = "dark",  -- dark, light, material
        font_size = 12,
        show_toolbar = true,
        show_statusbar = true,
        window_size = {1200, 800}
    }
}

return settings 