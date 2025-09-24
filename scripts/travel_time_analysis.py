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
        gtfs_folder / 'NW_bus_clipped.zip',
        gtfs_folder / 'SW_bus_clipped.zip',
        gtfs_folder / 'W_bus_clipped.zip',
        gtfs_folder / 'WM_bus_clipped.zip',
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
    Calculates and prints a detailed itinerary for a specific
    origin ID and destination ID.
    """
    departure_time = dt.datetime(2025, 9, 9, 12, 0, 0)
    
    # Select the specific origin and destination by their ID
    origin_point = origins_gdf[origins_gdf['id'] == origin_id].to_crs("EPSG:4326")
    destination_point = destinations_gdf[destinations_gdf['id'] == destination_id].to_crs("EPSG:4326")

    if origin_point.empty or destination_point.empty:
        print(f"Error: Could not find features with Origin ID {origin_id} or Destination ID {destination_id}.")
        return

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
        return

    # Print the details of the first option
    first_option = detailed_itineraries.iloc[0]
    print(f"\nRoute Option 1 ({first_option['total_time'].total_seconds() / 60:.1f} minutes):")
    
    segments = first_option['segments']
    for i, segment in enumerate(segments):
        mode = segment['mode']
        duration = segment['duration'].total_seconds() / 60
        distance = segment['distance']
        
        print(f"  Segment {i+1}: {mode.name}")
        print(f"    - Duration: {duration:.1f} minutes")
        print(f"    - Distance: {distance:.1f} meters")

        if 'wait_time' in segment:
            wait_time = segment['wait_time'].total_seconds() / 60
            print(f"    - Wait time: {wait_time:.1f} minutes")
        
        if 'route_short_name' in segment and segment['route_short_name']:
            print(f"    - Route: {segment['route_short_name']}")
            
    print("--------------------------------------")