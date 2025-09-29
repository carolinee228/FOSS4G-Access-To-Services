# FOSS4G Workshop: Public Transport Accessibility Analysis in QGIS

**Workshop Overview**

Welcome! This workshop will guide you through performing a public transport accessibility analysis using Python inside QGIS. We will calculate the travel time from a set of origins to a set of destinations using open-source tools and data.

---

## Prerequisites

Before you begin, you must have the following software:

1.  **QGIS (version 3.28 or newer)**: If you do not have it, download it from [qgis.org](https://qgis.org/en/site/forusers/download.html).
2.  **This GitHub Repository**: You need all the data and script files.

---

## 🚀 Setup Instructions (Crucial!)

This setup ensures QGIS can find the correct Java version and Python packages **without requiring admin rights or permanently changing your system settings**.

### Step 1: Download the Workshop Files

If you haven't already, download this repository as a ZIP file and extract it. This will create a folder likely named `foss4g-access-to-services-main`. For simplicity, you can rename this folder to `FOSS4G_Workshop` and place it in a memorable location, for example: `C:\Users\YourUser\FOSS4G_Workshop\` or `/home/user/foss4g_workshop/`.

### Step 2: Download and Place the Portable JDK (Java 21)

Our analysis library (`r5py`) requires a portable, 64-bit version of JDK 21.

1.  Go to the download page: [**Eclipse Temurin JDK 21 Downloads**](https://adoptium.net/temurin/releases/?version=21)
2.  On the download page, find your Operating System (Windows, macOS, Linux).
3.  Crucially, download the **Archive** file, which will be a `.zip` or `.tar.gz`. **Do NOT download the installer (`.msi` or `.pkg`).**
4.  Create a new folder named `jdk` inside your main workshop folder.
5.  Extract the contents of the downloaded archive into this new `jdk` folder.

### Step 3: Install Required Python Packages

QGIS comes with its own Python environment. You **must** install the required libraries directly into it using the specific instructions for your operating system below.

---

#### **For Windows Users**

1.  From the Start Menu, find and open the **"OSGeoW Shell"**.
2.  In the terminal window, run the following command:
    ```batch
    python-qgis-ltr -m pip install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```
3.  Wait for the installation to complete, then you can close the OSGeoW shell.

---

#### **For macOS Users**

1.  Open a new standard **Terminal**.
2.  Run the following command. This specifically targets the Python executable located inside the QGIS application bundle to ensure packages are installed in the correct place.
    ```bash
    /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```
3.  **Note:** The first time you run a command like this, your Mac may prompt you to install the "Xcode Command Line Developer Tools". Please accept this; it is a one-time setup that is required for installing many Python packages. The installation may take a few minutes. After it completes, re-run the command above if necessary.

---

#### **For Linux Users**

1.  Open a new standard **Terminal**.
2.  QGIS on Linux provides a specific command to access its Python environment. Run the following:
    ```bash
    python3-qgis -m pip install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```
3.  **Note:** Depending on your QGIS version, this command might be `python-qgis` or `python-qgis-ltr`.

---

### Step 4: Launch QGIS

For this workshop, you can launch QGIS normally from your Start Menu (Windows), Applications folder (macOS), or application menu (Linux). **The special terminal launch is no longer required.**

* **Note for macOS users:** The first time you open QGIS, your Mac's security settings (Gatekeeper) may block it. If this happens, go to **System Settings > Privacy & Security**, scroll down, and you will see a message about QGIS being blocked. Click the **"Open Anyway"** button.

---

## 💡 Workshop Steps: Interactive Analysis

After completing the setup, launch QGIS and open the Python Console (**Plugins -> Python Console**). The best way to run the following code blocks is to click the **Show editor** button, paste the code into the editor panel, then click the **Run Script** button for each step.

### Step 1: Set Up the Environment and Java Connection

This critical first step tells Python where your workshop folder is located and **manually configures the connection to the portable Java environment**. This new method is much more reliable for macOS.

```python
# --- Step 1: Set up the Environment ---
from pathlib import Path
import sys
import os
import jpype

# !!! IMPORTANT: YOU MUST EDIT THIS LINE !!!
# Change the path below to the location where you extracted the workshop files.
# Windows example: project_root = Path('C:/Users/YourUser/FOSS4G_Workshop')
# macOS/Linux example: project_root = Path('/home/user/foss4g_workshop')
project_root = Path('YOUR_WORKSHOP_FOLDER_PATH_HERE')

# --- Java Configuration (The Definitive macOS Fix) ---
# Find the portable JDK folder
jdk_folder = project_root / 'jdk'
# Find the first (and only) JDK directory inside
try:
    java_dir = next(jdk_folder.glob('*/'))
except StopIteration:
    raise FileNotFoundError(f"No JDK folder found inside {jdk_folder}. Please check your setup.")

# Explicitly set JAVA_HOME inside the script
os.environ['JAVA_HOME'] = str(java_dir)

# Construct the full path to the JVM library file, which differs by OS
jvm_path = None
if sys.platform == "darwin":  # macOS
    jvm_path = java_dir / "lib" / "server" / "libjvm.dylib"
elif sys.platform == "win32": # Windows
    jvm_path = java_dir / "bin" / "server" / "jvm.dll"
elif sys.platform.startswith("linux"): # Linux
    jvm_path = java_dir / "lib" / "server" / "libjvm.so"

if not jvm_path or not jvm_path.exists():
    raise FileNotFoundError(f"Could not find the JVM library file at {jvm_path}. Please check the JDK folder.")

# Start the JVM if it's not already running
if not jpype.isJVMStarted():
    print(f"Starting JVM from: {jvm_path}")
    jpype.startJVM(str(jvm_path), classpath=[])
else:
    print("JVM is already running.")


# --- Add scripts folder to Python's path ---
scripts_path = project_root / 'scripts'
if str(scripts_path) not in sys.path:
    sys.path.append(str(scripts_path))

print(f"Environment is ready. Project root set to: {project_root}")
```

### Step 2: Import Necessary Functions

```python
# --- Step 2: Import Necessary Functions ---
import geopandas as gpd
import pandas as pd
from travel_time_analysis import get_travel_time_matrix, build_transport_network
from workshop_utils import active_layer_to_gdf, add_gdf_to_qgis
print("Tools imported.")
```

### Step 3: Build the Transport Network

This is a one-time step that reads all the map and transit data into memory. It may take a minute or two.

```python
# --- Step 3: Build the Transport Network ---
print("Building the transport network, this may take a moment...")
transport_network = build_transport_network(project_root)
print("Transport network built successfully.")
```


### Step 4: Load Origin and Destination Layers

1.  **Load Data**: Add the `clipped_residential_properties.gpkg` and `clipped_gpmainsites.gpkg` files to QGIS from your workshop folder.
2.  **Select Origins**: Select the `clipped_residential_properties` layer in the Layers Panel.
3.  **Run Code**:

```python
# --- Step 4.1: Load Origin Layer ---
origins = active_layer_to_gdf()
```

4.  **Select Destinations**: Select the `clipped_gpmainsites` layer in the Layers Panel.
5.  **Run Code**:

```python
# --- Step 4.2: Load Destination Layer ---
destinations = active_layer_to_gdf()
```

### Step 5: Run the Travel Time Analysis

```python
# --- Step 5: Run the Travel Time Analysis ---
travel_time_df = get_travel_time_matrix(transport_network, origins, destinations)
print("Analysis complete! Result preview:")
print(travel_time_df.head())
```

### Step 6: Find the Quickest Route to Each Destination

```python
# --- Step 6: Find the Quickest Route ---
shortest_tt = travel_time_df.sort_values("travel_time").drop_duplicates("to_id")
print("Filtering complete. Result preview:")
print(shortest_tt.head())
```

### Step 7: Join Results Back to Destination Geometries

This step now includes the `from_id` so you can trace which origin connects to each destination.

```python
# --- Step 7: Join Results ---
results_gdf = destinations.merge(
    shortest_tt[["from_id", "travel_time", "to_id"]],
    left_on="id",
    right_on="to_id",
    how="left"
).drop(columns=["to_id"])
print("Join complete.")
```

### Step 8: Handle Unreachable Destinations

```python
# --- Step 8: Handle Unreachable ---
results_gdf['travel_time'] = results_gdf['travel_time'].fillna(90)
print("Unreachable destinations handled.")
```

### Step 9: Add the Final Layer to QGIS

```python
# --- Step 9: Add Layer to QGIS ---
add_gdf_to_qgis(results_gdf, "outbound_accessibility_results")
print("\nWorkshop complete! A new layer has been added to your project.")
```

---

## 🗺️ Exploring Further (Optional Tasks)

For those who finish early, here are some extra tasks to explore more capabilities of `r5py`.

### Task 1: Tweaking the Analysis Parameters

The core of the analysis happens in the `get_travel_time_matrix` function.

1.  In the QGIS Browser panel, navigate to your project folder, then into the `scripts` subfolder.
2.  Drag the `travel_time_analysis.py` file into the QGIS Python Editor window.
3.  Try changing some of the parameters inside the `r5py.TravelTimeMatrix` call (e.g., `max_time`, `departure_time`, `speed_walking`).
4.  Click the "Run Script" button in the editor to save the changes to memory.
5.  Now, re-run Step 5 from the main workshop guide above to see how your results change.

### Task 2: Calculate Inbound Journeys

Our main analysis was "outbound". Let's calculate the "inbound" journey time from reachable destinations back to our origins. This is a more efficient approach for large datasets as we only calculate return journeys for destinations we know we can get to.

Run the following code block in the QGIS Python Editor.

```python
# --- Task 2: Inbound Journey Analysis ---
print("\n--- Starting Inbound Analysis ---")

# Use the reachable destinations from the outbound analysis as the new origins
inbound_origins = results_gdf[results_gdf['travel_time'] < 90]
print(f"Found {len(inbound_origins)} reachable destinations to use as inbound origins.")

# The original origins are now the destinations for the inbound trip
inbound_destinations = origins.copy()

# Calculate inbound travel times
inbound_tt_df = get_travel_time_matrix(transport_network, inbound_origins, inbound_destinations)

# For each residential property (the 'to_id' in this result), find the quickest journey
shortest_inbound_tt = inbound_tt_df.sort_values("travel_time").drop_duplicates("to_id")

# Create a clean DataFrame with just the results we need for the join
inbound_results = shortest_inbound_tt[['from_id', 'to_id', 'travel_time']].copy()
inbound_results = inbound_results.rename(columns={
    "travel_time": "inbound_time",
    "from_id": "inbound_from_gp_id",
    "to_id": "id"  # Rename to 'id' to match the key in the 'origins' GeoDataFrame
})

# Ensure the join keys are the same data type
origins['id'] = origins['id'].astype('int64')
inbound_results['id'] = inbound_results['id'].astype('int64')

# Use a left merge to join the inbound results back to the original origins layer
inbound_results_gdf = origins.merge(inbound_results, on='id', how='left')

# Handle cases where no return journey was found
inbound_results_gdf['inbound_time'] = inbound_results_gdf['inbound_time'].fillna(90)

# Add the results to QGIS. This layer will have a point for every residential property.
add_gdf_to_qgis(inbound_results_gdf, "inbound_accessibility_results")

print("\n--- Inbound Analysis Complete ---")
print("A new 'inbound_accessibility_results' layer has been added.")
```

### Task 3: Get a Detailed Point-to-Point Itinerary

Let's find the specific turn-by-turn route between one origin and one destination and visualize it on the map.

1.  Open the attribute table for the **`outbound_accessibility_results`** layer in QGIS.
2.  Find an interesting row (one with a `travel_time` less than 90). Note down the value from the **`from_id`** column (this is your origin) and the **`id`** column (this is your destination).
3.  Copy the code below into the QGIS editor.
4.  **Replace the placeholder `0` values** with the `from_id` and `id` numbers you found.
5.  Run the script.

```python
# --- Task 3: Run Detailed Itinerary ---
from travel_time_analysis import get_detailed_itinerary_by_id

# !!! CHANGE THESE ID VALUES to match a specific origin and destination !!!
start_id = 0
end_id = 0

# This function now returns a GeoDataFrame of the route segments
detailed_route_gdf = get_detailed_itinerary_by_id(transport_network, origins, destinations, start_id, end_id)

# Add the route to the map if it was found
if detailed_route_gdf is not None and not detailed_route_gdf.empty:
    add_gdf_to_qgis(detailed_route_gdf, f"route_{start_id}_to_{end_id}")
    print(f"Added detailed route from {start_id} to {end_id} to the map.")
```

---

## 🏛️ Project Context and Methodology

For those interested in the real-world application of this workshop, we have prepared a separate document detailing the data sources and the methodology used to scale this analysis up for a national project.

[**Read more about the Data Sources and Production Methodology here.**](CONTEXT.md)
