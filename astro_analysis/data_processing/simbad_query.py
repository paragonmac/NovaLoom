import time
import pandas as pd
from astroquery.simbad import Simbad

def query_simbad(world_coords, sources_df, search_radius, timeout, min_flux=0):
    """
    Query Simbad for star names and object types.
    
    Parameters:
    -----------
    world_coords : list
        List of SkyCoord objects
    sources_df : pandas.DataFrame
        DataFrame containing source information
    search_radius : astropy.units.Quantity
        Search radius for Simbad queries
    timeout : int
        Timeout in seconds for Simbad queries
    min_flux : float
        Minimum flux threshold for querying sources
        
    Returns:
    --------
    pandas.DataFrame
        Updated DataFrame with Simbad information
    """
    Simbad.TIMEOUT = timeout
    Simbad.add_votable_fields('otype(V)')
    
    star_names = []
    object_types = []
    query_count = 0
    skipped_low_flux = 0
    simbad_errors = 0
    start_time = time.time()
    
    for i, coord in enumerate(world_coords):
        # Skip faint sources
        source_flux = sources_df.loc[i, 'flux'] if 'flux' in sources_df.columns else min_flux
        if source_flux < min_flux:
            star_names.append(None)
            object_types.append(None)
            skipped_low_flux += 1
            continue
            
        query_count += 1
        simbad_name = None
        simbad_otype = None
        
        try:
            result_table = Simbad.query_region(coord, radius=search_radius)
            
            if result_table is not None and len(result_table) > 0:
                name = result_table['MAIN_ID'][0]
                otype = result_table['OTYPE_V'][0]
                
                if isinstance(name, bytes): name = name.decode('utf-8')
                if isinstance(otype, bytes): otype = otype.decode('utf-8')
                
                simbad_name = name
                simbad_otype = otype
                
        except Exception as e:
            simbad_errors += 1
            if simbad_errors < 10:
                print(f"Warning: Simbad query failed for source {i}: {type(e).__name__}")
            simbad_name = "Query Error"
            simbad_otype = "Error"
            
        star_names.append(simbad_name)
        object_types.append(simbad_otype)
        
        # Polite delay
        time.sleep(0.2)
        
        # Progress indicator
        if query_count % 25 == 0 and query_count > 0:
            elapsed = time.time() - start_time
            print(f"Queried {query_count} sources ({elapsed:.1f}s)...")
            
    # Add results to DataFrame
    sources_df['simbad_name'] = star_names
    sources_df['simbad_otype'] = object_types
    
    return sources_df 