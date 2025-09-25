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
    Takes a GeoDataFrame, creates a QGIS memory layer from it,
    and adds it to the current QGIS project.
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame.")

    print(f"Adding GeoDataFrame as a new layer named '{layer_name}'...")

    # Determine geometry type from the GeoDataFrame
    geom_type = gdf.geom_type.unique()[0]
    qgis_geom_type = 'Unknown'
    if 'Point' in geom_type:
        qgis_geom_type = 'Point'
    elif 'Line' in geom_type:
        qgis_geom_type = 'LineString'
    elif 'Polygon' in geom_type:
        qgis_geom_type = 'Polygon'
    
    crs_string = gdf.crs.to_string()
    uri = f"{qgis_geom_type}?crs={crs_string}"
    
    # Create the memory layer with a defined geometry and CRS
    temp_layer = QgsVectorLayer(uri, layer_name, "memory")
    provider = temp_layer.dataProvider()

    # Add attribute fields from the GeoDataFrame, mapping types to QGIS types
    fields_to_add = []
    dtype_map = {
        'int64': QVariant.Int,
        'float64': QVariant.Double,
        'object': QVariant.String,
        'bool': QVariant.Bool
    }
    for col_name, dtype in gdf.drop(columns=['geometry']).dtypes.items():
        variant_type = dtype_map.get(dtype.name, QVariant.String) # Default to String
        fields_to_add.append(QgsField(col_name, variant_type))
    
    provider.addAttributes(fields_to_add)
    temp_layer.updateFields()

    # Add features to the layer
    features = []
    for _, row in gdf.iterrows():
        feature = QgsFeature()
        # Ensure geometry is valid before creating the QGIS geometry object
        if row.geometry and not row.geometry.is_empty:
            geom = QgsGeometry.fromWkt(row.geometry.wkt)
            feature.setGeometry(geom)
        
        # Set attributes, converting any pandas NaN/NaT to None for QGIS
        attributes = []
        for col_name in gdf.drop(columns=['geometry']).columns:
            value = row[col_name]
            if pd.isna(value):
                attributes.append(None)
            else:
                attributes.append(value)
        feature.setAttributes(attributes)
        features.append(feature)
        
    provider.addFeatures(features)
    temp_layer.updateFields()

    # Add layer to the project
    QgsProject.instance().addMapLayer(temp_layer)
    print(f"Layer '{layer_name}' added successfully.")
    return temp_layer