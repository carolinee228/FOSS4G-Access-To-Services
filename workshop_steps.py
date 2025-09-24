# ===================================================================
# FOSS4G Workshop: Public Transport Accessibility Analysis
# ===================================================================
# Instructions: Run each numbered step in the QGIS Python Console.

# --- Step 1: Set up the Environment ---
# This first step tells Python where to find our custom scripts.
print("--- Step 1: Setting up environment ---")
from pathlib import Path
import sys
project_root = Path.cwd()
scripts_path = project_root / 'scripts'
if str(scripts_path) not in sys.path:
    sys.path.append(str(scripts_path))
print("Environment is ready.")

# --- Step 2: Import Necessary Functions ---
# Now we import all the tools we'll need for our analysis.
print("\n--- Step 2: Importing tools ---")
import geopandas as gpd
from single_core_ttm import single_core_ttm
from workshop_utils import active_layer_to_gdf, add_gdf_to_qgis
print("Tools imported.")

# --- Step 3: Load Origin and Destination Layers ---
# Select your ORIGINS layer in the QGIS Layers Panel, then run this line.
print("\n--- Step 3: Loading data ---")
print("ACTION: Please select your ORIGINS layer (e.g., residential properties) and press Enter.")
origins = active_layer_to_gdf()

# Now, select your DESTINATIONS layer in the QGIS Layers Panel and run this line.
print("\nACTION: Please select your DESTINATIONS layer (e.g., GP sites) and press Enter.")
destinations = active_layer_to_gdf()

# --- Step 4: Run the Travel Time Analysis ---
# This is the core of our workshop. It may take a few minutes.
print("\n--- Step 4: Calculating travel times (this may take a moment)... ---")
travel_time_df = single_core_ttm(origins, destinations)
print("Analysis complete! The result is a table of all possible journey times.")
print("Result preview:")
print(travel_time_df.head())

# --- Step 5: Find the Quickest Route to Each Destination ---
# The result has many routes. We only want the fastest one for each destination.
print("\n--- Step 5: Filtering for the quickest route to each destination ---")
shortest_tt = travel_time_df.sort_values("travel_time").drop_duplicates("to_id")
print("Filtering complete.")
print("Result preview:")
print(shortest_tt.head())

# --- Step 6: Join Results Back to Destination Geometries ---
# Let's join the travel time data back to our original destination points.
print("\n--- Step 6: Joining travel times back to the destination layer ---")
# We use a 'left' merge to keep all original destinations, even if no route was found.
results_gdf = destinations.merge(
    shortest_tt[["travel_time", "to_id"]],
    left_on="id",
    right_on="to_id",
    how="left"
).drop(columns=["to_id"])
print("Join complete.")

# --- Step 7: Add the Final Layer to QGIS ---
# The final step is to visualize our results on the map!
print("\n--- Step 7: Adding results to the QGIS map ---")
add_gdf_to_qgis(results_gdf, "outbound_accessibility_results")
print("\nWorkshop complete! A new layer has been added to your project.")