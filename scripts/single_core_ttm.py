from pathlib import Path
import datetime as dt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import r5py

def single_core_ttm(origins, destinations):
    """Calculates a travel time matrix using a relative path for data."""
    
    # --- 1. Find the data directory relative to the project root ---
    # Path.cwd() gets the directory from which QGIS was launched.
    project_root = Path.cwd()
    data_path = project_root / 'network_data'

    # Add a check to make sure the folder is found
    if not data_path.exists():
        raise FileNotFoundError(
            f"Could not find the 'network_data' directory. "
            f"Expected it to be in: {project_root}"
        )

    # --- 2. Define File Paths ---
    pbf_path = data_path / 'clipped.osm.pbf'
    gtfs_folder = data_path / 'gtfs'
    
    gtfs_paths = [
        gtfs_folder / 'NW_bus_clipped.zip',
        gtfs_folder / 'SW_bus_clipped.zip',
        gtfs_folder / 'W_bus_clipped.zip',
        gtfs_folder / 'WM_bus_clipped.zip',
    ]

    missing = [p for p in [pbf_path, *gtfs_paths] if not Path(p).exists()]
    if missing:
        raise FileNotFoundError("Missing network files:\n" + "\n".join(str(p) for p in missing))
    
    transport_network = r5py.TransportNetwork(str(pbf_path), gtfs_paths, allow_errors=True)
    
    # --- Clean the Input Geometries ---
    # This new section fixes the MultiPoint error
    print("Cleaning input geometries...")
    origins['geometry'] = origins.geometry.centroid
    destinations['geometry'] = destinations.geometry.centroid
    print("Geometries converted to centroids.")

    def to_epsg4326_gdf(df):
        
        if isinstance(df, gpd.GeoDataFrame):
            if df.crs is None:
                raise ValueError("GeoDataFrame has no CRS; set the correct CRS before calling r5py.")
            return df.to_crs("EPSG:4326")

        # Plain DataFrame
        if {"lon", "lat"}.issubset(df.columns):  # WGS84 lon/lat
            gdf = gpd.GeoDataFrame(
                df.copy(),
                geometry=gpd.points_from_xy(df["lon"], df["lat"]),
                crs="EPSG:4326"
            )
            return gdf
        
        
    #call unpack list function for origins and destinations 
    origins_gdf = to_epsg4326_gdf(origins)
    destinations_gdf = to_epsg4326_gdf(destinations)

        # You could perform spatial operations here, e.g.,
        # gdf['area'] = gdf.geometry.area # (Only makes sense if geometry isn't points)
        # gdf.to_file('output.shp') # Directly write to a shapefile (requires Fiona)


        # --- 6. Output ---
        # As this is a function, the modified 'feature' (with new attributes)
        # is automatically passed downstream. If you needed to output features
        # per row of the GDF, you'd use a Class structure and self.pyoutput().

    

    if origins is not None:
        #mode_str=FME_MacroValues['TRANSPORT_MODES']
        departure_time = dt.datetime(2025, 9, 9, 12, 0, 0)
        transport_modes = [r5py.TransportMode.TRANSIT]
        percentiles = [50]
        assert all(isinstance(p, int) and 0 <= p < 100 for p in percentiles)
        
        #logging.basicConfig(level=logging.DEBUG)
        
        #self.log.logMessageString(f"Calculating walkout TravelTimeMatrix with {len(origins)} origins, {len(destinations)} destinations", fmeobjects.FME_INFORM)
        travel_times = r5py.TravelTimeMatrix(
            transport_network,
            origins=origins_gdf,
            destinations=destinations_gdf,
            max_time=dt.timedelta(minutes=90),
            departure=departure_time,
            departure_time_window=dt.timedelta(minutes=60),
            transport_modes=transport_modes,
            max_time_walking=dt.timedelta(minutes=20),
            percentiles = percentiles,
            speed_walking=4.5)
        
        #self.log.logMessageString(f"Processing results...", fmeobjects.FME_INFORM)

        print("printing travel times")
        print(travel_times)


        travel_times = travel_times.dropna(subset=['travel_time'])

        out_csv = r"C:\Users\routing_admin\Downloads\travel_times.csv"
        travel_times.to_csv(out_csv, index=False)
        print("Wrote:", out_csv)
        
    

        if travel_times is not None and not travel_times.empty:
            for index, row in travel_times.iterrows():
                travel_time_val = row['travel_time']
                
                #new_feature = fmeobjects.FMEFeature()

                
                converted_travel_time = pd.Timedelta(travel_time_val).total_seconds() / 60
                #print(travel_time_val)
                #new_feature.setAttribute('travel_time_test', float(travel_time_val))

                    #Set origin id 
                # if 'id' in row:
                    # new_feature.setAttribute('origin_id', row['id'])
                #else:
                    #  new_feature.setAttribute('origin_id', 'unknown')
                    
                from_id=row['from_id']
                to_id=row['to_id']
                return travel_times
                
                
                #cutoff_str = ",".join(str(c) for c in cutoffs)
                # mode_str = ",".join(m.name.lower() for m in transport_modes)
                #departure_str = departure_time.strftime("%Y-%m-%d %H:%M:%S")

                # new_feature.setAttribute("cutoffs", cutoff_str)
                # new_feature.setAttribute("transit_mode", mode_str)
                #new_feature.setAttribute("departure_time", departure_str)
                #new_feature.setAttribute("run_id", run_id)
                #new_feature.setAttribute("from_id", from_id)
                #new_feature.setAttribute("to_id", to_id)

                #shapely_geom = row['geometry']
                #geom_wkb = shapely_geom.wkb
                #new_feature.setAttribute('wkb_geometry', geom_wkb)

                #pyoutput(new_feature)
