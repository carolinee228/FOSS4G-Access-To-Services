from qgis.core import (
    QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry
)
import pandas as pd
import geopandas as gpd

def active_layer_to_gdf(iface, id_field=None, selected_only=False, to_crs="EPSG:4326"):
    layer = iface.activeLayer()
    if not layer or not layer.isValid():
        raise RuntimeError("No valid active layer.")
    if layer.geometryType() == -1:
        raise RuntimeError("Active layer has no geometry.")

    src_crs = layer.crs()
    dst_crs = QgsCoordinateReferenceSystem(to_crs)
    xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

    feats = layer.getSelectedFeatures() if selected_only else layer.getFeatures()
    field_names = [f.name() for f in layer.fields()]
    use_attr_id = id_field in field_names if id_field else False

    rows = []
    for f in feats:
        geom = f.geometry()
        if not geom or geom.isEmpty():
            continue
        g = QgsGeometry(geom)
        if src_crs != dst_crs:
            g.transform(xform)
        rid = f[id_field] if use_attr_id else f.id()
        rows.append({"id": rid, "lat": g.asPoint().y(), "lon": g.asPoint().x(), "wkt":g.asWkt()})

    if not rows:
        return gpd.GeoDataFrame(columns=["id", "geometry"], crs=to_crs)

    df = pd.DataFrame(rows)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df["wkt"]), crs=to_crs)
    return gdf[["id", "lat", "lon", "geometry"]]
    
