# FOSS4G-Access-To-Services
**Workshop Overview**
XYZ 
**Pre-Requisites / To Do Beforehand**
XYZ
**How To Run Access To Services**
1. Ensure you have QGIS installed and either cloned or downloaded this repo so that you have the following files available:
    - **GTFS Data:**
   - W_bus_clipped
   - WM_bus_clipped
   - SW_bus_clipped
   - NW_bus_clipped
   - **OSM PBF file (binary format used to store data from OpenStreetMap (OSM))**
   - clipped.osm.pbf
   - **Origin Points File**
   - clipped_gpmainsites.gpkg
   - **Destination Points File**
   - clipped_residential_properties.gpkg
   - **Python Files to Run Access To Services**
   - active_layer.py (This allows users to set the origin and destination files in QGIS based on which layer is selected in the Table of Contents)
   - single_core_ttm.py (This is the Travel Time Analysis using r5py. This will calculate travel times between origins and destinations)
   - shortest_destination.py (This will keep only one origin per destination based on the shortest travel time)
   - gdf_to_qgslayer.py (converts the merged GDF to a QGIS layer)

2. In QGIS, open a blank project. Along the top bar, go to Plugins > Python Console. This will open the Python Console at the bottom of the screen
3. At the top of the Python Console, open the Editor. There should be an icon to 'Show Editor' which will open the Python Editor on the right of the screen
4. In the Editor, you can now open the four Python files from the repo. You can do this by going to the Editor and finding the icon for 'Open Script'. They will then open in the Editor as separate files
5. Now, import the Origin and Destination files into the Table of Contents in QGIS. From the Repo, make sure clipped_gpmainsites.gpkg and clipped_residential_properties.gpkg are present, these will be the origin and destination points respectfully
6. This may be a good time to add a basemap in as well. In the Browser, scroll down to XYZ Tiles and find OpenStreetMap. You can right-click this layer to Add Layer to Project
7. Now, we want to set the Origin points for Python to use. In the Table of Contents, click on the clipped_gpmainsites.gpkg layer so that it is selected. Then, in the Editor, ensure you open the active_layer.py file and click the icon to 'Run Script'. Next, in the actual Python Console, run the following command `origins = active_layer_to_gdf(iface)`. This should now set the Origins. You can double check origins have been set by just typing `origins` into the Python Console > Enter and check results appear as expected
8. Now, we want to set the Destination points for Python to use. In the Table of Contents, click on the clipped_residential_properties.gpkg layer so that it is selected. This is really important that this new layer is now selected. Then, in the Editor, ensure you open the active_layer.py file and click the icon to 'Run Script'. Next, in the actual Python Console, run the following command `destinations = active_layer_to_gdf(iface)`. This should now set the Destinations. You can double check destinations have been set by just typing `destinations` into the Python Console > Enter and check results appear as expected
9. Next, we are going to calculate the travel times between the origin and destination points. In the Editor, open the single_core_ttm.py file and 'Run Script'. We can then call the function and calculate the travel times by going back to the Python Console and typing `single_core_ttm(origins,destinations)`. This should return values for where the routing came from, and where the routing went to, and the time in minutes for this to occur. NOTE - FOR TESTING, YOU WILL NEED TO CHANGE THE SCRIPT IN THE EDITOR. AT THE MOMENT, THE OSM PBF FILE PATH AND THE GTFS FILE PATH ARE HARDCODED AND WILL NOT WORK ON OTHER MACHINES, ENSURE TO CHANGE THIS FILE PATH IN THE EDITOR FOR THIS SINGLE_CORE_TTM SCRIPT TO POINT TO WHERE YOU HAVE DOWNLOADED THE OSM PBF FILE AND GTFS FILES
10. Next, we want to ensure that we only keep the shortest origin point per destination. In this example of GPs, we only want to keep the GP that is closest to any given house as this would be the GP they would frequent. To do this, in the console, you can run `shortest_tt = tt.sort_values("travel_time").drop_duplicates("to_id")`. To inspect the results, in the console, type and then enter `shortest_tt`
11. We then need to merge the geometry from the original destinations layer back on to the travel times, as the result from our calculation is non-spatial. In the Console, we can run the following `merged = destinations.merge(shortest_tt[["travel_time","to_id"]],left_on="id", right_on="to_id",how="left").drop(columns=["to_id"])`. As before, you can view the results in the Console by typing and entering `merged`
12. We would then like to display our results on the map. In the Editor, navigate to the gdf_to_qgslayer.py and Run Script. Next, back in the Console, enter `add_gdf_to_qgis(merged, "outbound_results")`. This will add the results to the map as a layer in the Table of Contents called 'Outbound Results'.

