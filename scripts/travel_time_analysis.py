from pathlib import Path
import datetime as dt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import r5py

def build_transport_network(project_root):
    """
    Builds the r5py TransportNetwork object from data files.
    This is a time-consuming step and should only be done once per session.
    """
    data_path = project_root / 'network_data'
    if not data_path.exists():
        raise FileNotFoundError(
            f"Could not find the 'network_data' directory. "
            f"Expected it to be in: {project_root}"
        )

    pbf_path = data_path / 'clipped.osm.pbf'
    gtfs_folder = data_path / 'gtfs'
    
    gtfs_paths = [
        gtfs_folder / 'bus_gtfs_cardiff.zip',
        gtfs_folder / 'train_gtfs_cardiff.zip',
    ]

    transport_network = r5py.TransportNetwork(
        str(pbf_path), 
        [str(p) for p in gtfs_paths], 
        allow_errors=True
    )
    return transport_network


def get_travel_time_matrix(transport_network, origins, destinations):
    """
    Calculates a travel time matrix using a pre-built transport network.
    """
    # Clean the Input Geometries (convert to centroids)
    origins_cleaned = origins.copy()
    destinations_cleaned = destinations.copy()
    origins_cleaned['geometry'] = origins_cleaned.geometry.centroid
    destinations_cleaned['geometry'] = destinations_cleaned.geometry.centroid

    # Reproject data to WGS84 (EPSG:4326) for r5py
    origins_gdf = origins_cleaned.to_crs("EPSG:4326")
    destinations_gdf = destinations_cleaned.to_crs("EPSG:4326")

    # Set Routing Parameters
    departure_time = dt.datetime(2025, 9, 9, 12, 0, 0)
    transport_modes = [r5py.TransportMode.TRANSIT]
    percentiles = [50]

    # Calculate the Travel Time Matrix
    travel_times_computer = r5py.TravelTimeMatrix(
        transport_network,
        origins=origins_gdf,
        destinations=destinations_gdf,
        max_time=dt.timedelta(minutes=90),
        departure=departure_time,
        departure_time_window=dt.timedelta(minutes=60),
        transport_modes=transport_modes,
        max_time_walking=dt.timedelta(minutes=20),
        percentiles=percentiles,
        speed_walking=4.5
    )
    
    return travel_times_computer

def get_detailed_itinerary_by_id(transport_network, origins_gdf, destinations_gdf, origin_id, destination_id):
    """
    Calculates and returns a GeoDataFrame of route segments for a specific
    origin ID and destination ID.
    """
    import datetime as dt
    import r5py

    departure_time = dt.datetime(2025, 9, 9, 12, 0, 0)
    
    # Select the specific origin and destination by their ID
    origin_point_raw = origins_gdf[origins_gdf['id'] == origin_id]
    destination_point_raw = destinations_gdf[destinations_gdf['id'] == destination_id]

    if origin_point_raw.empty or destination_point_raw.empty:
        print(f"Error: Could not find features with Origin ID {origin_id} or Destination ID {destination_id}.")
        return None

    # Clean the geometries to ensure they are Points (using centroid)
    origin_point = origin_point_raw.copy()
    origin_point['geometry'] = origin_point.geometry.centroid
    destination_point = destination_point_raw.copy()
    destination_point['geometry'] = destination_point.geometry.centroid

    # Reproject to WGS84 for r5py
    origin_point = origin_point.to_crs("EPSG:4326")
    destination_point = destination_point.to_crs("EPSG:4326")

    print(f"\n--- Calculating Detailed Itinerary ---")
    print(f"From origin ID: {origin_id} to destination ID: {destination_id}")

    detailed_itineraries = r5py.DetailedItineraries(
        transport_network,
        origins=origin_point,
        destinations=destination_point,
        transport_modes=[r5py.TransportMode.TRANSIT],
        departure=departure_time,
        departure_time_window=dt.timedelta(minutes=60),
        max_time_walking=dt.timedelta(minutes=20),
    )

    if detailed_itineraries.empty:
        print("No route found within the given parameters.")
        return None

    # Filter for the first travel option (option 0)
    first_option_segments = detailed_itineraries[detailed_itineraries['option'] == 0].copy()
    
    print(f"Route found with {len(first_option_segments)} segments.")
    
    return first_option_segments
