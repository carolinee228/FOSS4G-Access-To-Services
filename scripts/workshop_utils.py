import geopandas as gpd
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsField
from qgis.utils import iface
from PyQt5.QtCore import QVariant
import pandas as pd

def active_layer_to_gdf():
    """
    Gets the currently selected layer in QGIS and returns it as a GeoDataFrame.
    Raises an error if no layer is selected.
    """
    layer = iface.activeLayer()
    if not layer:
        raise ValueError("No layer selected in QGIS. Please select a layer first.")
    
    print(f"Reading features from layer: '{layer.name()}'...")
    
    features = layer.getFeatures()
    gdf = gpd.GeoDataFrame.from_features(features, crs=layer.crs().toWkt())
    
    # Ensure a unique 'id' column exists for joining later
    if 'id' not in gdf.columns:
        gdf['id'] = range(len(gdf))

    print(f"Successfully read {len(gdf)} features.")
    return gdf

def add_gdf_to_qgis(gdf, layer_name="results"):
    """
    Takes a GeoDataFrame, cleans complex data types, saves it to a temporary
    GeoPackage, and adds it as a new layer to the current QGIS project.
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame.")

    print(f"Preparing and adding GeoDataFrame as a new layer named '{layer_name}'...")
    
    # Create a cleaned copy to avoid modifying the original DataFrame
    gdf_to_save = gdf.copy()

    for col in gdf_to_save.columns:
        # Don't touch the geometry column
        if col == gdf_to_save.geometry.name:
            continue
            
        # Convert timedelta objects to minutes (float)
        if pd.api.types.is_timedelta64_ns_dtype(gdf_to_save[col]):
            gdf_to_save[col] = gdf_to_save[col].dt.total_seconds() / 60
            
        # Convert any other problematic 'object' types (like r5py enums) to strings
        elif gdf_to_save[col].dtype == 'object':
             gdf_to_save[col] = gdf_to_save[col].astype(str)

    # Define a path for the temporary GeoPackage in the project's root directory
    project_root = Path.cwd()
    temp_gpkg_path = str(project_root / f"{layer_name}.gpkg")

    try:
        # Save the cleaned GeoDataFrame to the GeoPackage file
        gdf_to_save.to_file(temp_gpkg_path, driver='GPKG', layer=layer_name)
    except Exception as e:
        print(f"ERROR during file save operation: {e}")
        return None

    # Add the newly created GeoPackage layer to the QGIS interface
    added_layer = iface.addVectorLayer(temp_gpkg_path, layer_name, "ogr")

    if not added_layer or not added_layer.isValid():
        print(f"Error: QGIS could not add the layer from {temp_gpkg_path}")
        return None
        
    if added_layer.featureCount() == 0:
        print(f"WARNING: Layer was added to QGIS but contains 0 features. Check for data type issues in the source GeoDataFrame.")
    else:
        print(f"SUCCESS: Layer added to QGIS with {added_layer.featureCount()} features.")

    return added_layer
