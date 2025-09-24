# In FOSS4G/scripts/workshop_utils.py

import geopandas as gpd
from qgis.core import QgsVectorLayer, QgsProject
from qgis.utils import iface

def active_layer_to_gdf():
    """
    Gets the currently selected layer in QGIS and returns it as a GeoDataFrame.
    Raises an error if no layer is selected.
    """
    layer = iface.activeLayer()
    if not layer:
        raise ValueError("No layer selected in QGIS. Please select the origins layer.")
    
    print(f"Reading features from layer: '{layer.name()}'...")
    
    # Create a GeoDataFrame from the QGIS layer
    features = layer.getFeatures()
    gdf = gpd.GeoDataFrame.from_features(features)
    gdf.crs = layer.crs().toWkt()
    
    # Ensure a unique 'id' column exists for joining later
    if 'id' not in gdf.columns:
        gdf['id'] = range(len(gdf))

    print(f"Successfully read {len(gdf)} features.")
    return gdf

def add_gdf_to_qgis(gdf, layer_name="results"):
    """
    Takes a GeoDataFrame, saves it to a temporary GeoPackage,
    and adds it as a new layer to the current QGIS project.
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame.")

    print(f"Adding GeoDataFrame as a new layer named '{layer_name}'...")

    # Define a temporary path
    temp_path = f"memory://{layer_name}"

    # Convert GeoDataFrame to a QGIS Vector Layer
    # This avoids saving a file and is faster
    temp_layer = QgsVectorLayer(gdf.to_wkb().to_wkt(), layer_name, "memory")
    temp_layer.dataProvider().addAttributes([field for field in gdf.columns if field != 'geometry'])
    temp_layer.updateFields()
    
    feats = []
    for idx, row in gdf.iterrows():
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromWkb(row.geometry.wkb))
        feat.setAttributes(row.drop('geometry').tolist())
        feats.append(feat)
        
    temp_layer.dataProvider().addFeatures(feats)

    # Add the layer to the project
    QgsProject.instance().addMapLayer(temp_layer)
    print("Layer added successfully.")
    return temp_layer