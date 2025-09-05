from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsFields, QgsField, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
import geopandas as gpd

def add_gdf_to_qgis(gdf, layer_name):
    """
    Adds a GeoDataFrame as a new vector layer to the QGIS map.

    Args:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to be added.
        layer_name (str): The name for the new layer in QGIS.
    """
    if gdf.empty:
        print("GeoDataFrame is empty. No layer added.")
        return

    # Create an empty memory layer
    # We'll use the geometry type from the first non-empty feature
    first_valid_geom = gdf.geometry.loc[~gdf.geometry.is_empty].iloc[0]
    qgis_geom_type = first_valid_geom.geometryType()

    if 'travel_time' in gdf.columns:
        gdf['travel_time'] = gdf['travel_time'].fillna(90)

    # Create the QgsFields object from the GeoDataFrame's columns
    fields = QgsFields()
    for col, dtype in gdf.drop(columns=gdf.geometry.name).dtypes.items():
        qgis_type = QVariant.String
        if 'int' in str(dtype):
            qgis_type = QVariant.Int
        elif 'float' in str(dtype):
            qgis_type = QVariant.Double
        fields.append(QgsField(col, qgis_type))

    # Create the layer and set its CRS
    crs_wkt = gdf.crs.to_wkt()
    qgis_layer = QgsVectorLayer(f"{qgis_geom_type}?crs={crs_wkt}", layer_name, "memory")
    qgis_layer.dataProvider().addAttributes(fields)
    qgis_layer.updateFields()

    if not qgis_layer.isValid():
        print("Layer failed to load!")
        return

    # Add the features
    features = []
    for _, row in gdf.iterrows():
        feature = QgsFeature()
        qgis_geom = QgsGeometry.fromWkt(row.geometry.wkt)
        feature.setGeometry(qgis_geom)
        feature.setAttributes(row.drop(gdf.geometry.name).tolist())
        features.append(feature)

    qgis_layer.dataProvider().addFeatures(features)

    # Add the layer to the current QGIS project
    QgsProject.instance().addMapLayer(qgis_layer)
    print(f"Layer '{layer_name}' added successfully.")
