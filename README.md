# FOSS4G Workshop: Public Transport Accessibility Analysis in QGIS

**Workshop Overview**

Welcome! This workshop will guide you through performing a public transport accessibility analysis using Python inside QGIS. We will calculate the travel time from a set of origins to a set of destinations using open-source tools and data.

---

## Prerequisites

If possible, please complete these steps before attending the workshop.
Before you begin, you must have the following software:

1. **QGIS (version 3.28 or newer)**: If you do not have it, download it from [qgis.org](https://qgis.org/en/site/forusers/download.html).
2. **This GitHub Repository**: You need all the data and script files. Either clone or download the repo as a zip (and extract)

---

## Setup Instructions

This setup ensures QGIS can find the correct Java version and Python packages **without requiring admin rights or permanently changing your system settings**.

### Step 1: Download the Workshop Files

If you haven't already, download this repository as a ZIP file and extract it to a simple, memorable path with **no spaces**, for example: `C:\Users\YourUser\FOSS4G_Workshop\` or `/home/user/foss4g_workshop/`.

### Step 2: Download and Place the Portable JDK (Java 21)

Our analysis library (`r5py`) requires a portable, 64-bit version of JDK 21.

1. Go to the download page: [**Eclipse Temurin JDK 21 Downloads**](https://adoptium.net/temurin/releases/?version=21)
2. On the download page, find your Operating System (Windows, macOS, Linux).
3. Crucially, download the **Archive** file, which will be a `.zip` or `.tar.gz`. **Do NOT download the installer (`.msi` or `.pkg`).** For example, the Windows installer is found here: <img width="2267" height="1336" alt="image" src="https://github.com/user-attachments/assets/d8108635-4dcb-4de0-b1e2-8c4561c3d63f" />

4. Create a new folder named `jdk` inside your main workshop folder.
5. Extract the contents of the downloaded archive into this new `jdk` folder.

### Step 3: Configure Environment and Launch QGIS

This is the final setup step. We will open a terminal, install the necessary Python packages, temporarily tell the terminal where to find our portable Java, and then launch QGIS from that same session.

---

#### **For Windows Users**

For Windows, we will perform all the remaining setup steps in a single terminal window.

1. From the Start Menu, find and open the **"OSGeo4W Shell"**.
2. **Install Python Packages:** In the terminal window that opens, run the following command to install the required libraries into QGIS's Python environment.

    ```batch
    python-qgis-ltr -m pip install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```

3. **Navigate to your workshop folder.** After the installation completes, use the `cd` command. **Note: The exact folder name may differ slightly - may need to update to /foss4g-access-to-services**

    ```batch
    cd C:\Users\YourUser\FOSS4G_Workshop
    ```

4. **Set the `JAVA_HOME` variable.** This command points to the `jdk` folder you created. It is only active for this specific terminal window. **Note: The version number in the path below might be slightly different for you.**

    ```batch
    set "JAVA_HOME=%cd%\jdk\jdk-21.0.8+9"
    ```

5. **Launch QGIS.** **Note: You may need to adjust the path below to match your QGIS installation version.**

    ```batch
    qgis-ltr travel_time_workshop.qgz
    ```

---

#### **For macOS and Linux Users**

Open a Terminal window and run the following commands.

1. **Install Python Packages.**

    ```bash
    pip3 install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```

    * **Note for macOS users:** The first time you run this, your Mac may prompt you to install the "Xcode Command Line Developer Tools". Please accept this; it is a one-time setup that is required for installing many Python packages. The installation may take a few minutes. After it completes, re-run the `pip3 install...` command above.

2. **Navigate to your workshop folder.** **Note:** The exact folder name may vary slightly.

    ```bash
    cd /home/user/foss4g_workshop
    ```

3. **Set the `JAVA_HOME` variable.** **Note:** This command will not produce any output, which is normal. The exact folder name inside `jdk/` may vary slightly.

    ```bash
    export JAVA_HOME="$PWD/jdk/temurin-21.jdk/Contents/Home"
    ```

4. **Launch QGIS.**

    * **macOS**: `open /Applications/QGIS.app travel_time_workshop.qgz`
    * **Linux**: `qgis travel_time_workshop.qgz`
    * **Note for macOS users:** The first time you open QGIS, your Mac's security settings (Gatekeeper) may block it. If this happens, go to **System Settings > Privacy & Security**, scroll down, and you will see a message about QGIS being blocked. Click the **"Open Anyway"** button.

---

## Workshop Steps: Interactive Analysis

After completing the setup, launch QGIS from your configured terminal and open the Python Console (**Plugins -> Python Console**). The best way to run the following code blocks is to click the **Show editor** button, paste the code into the editor panel, then click the **Run Script** button for each step.

### Step 1: Set Up the Environment

This step identifies your workshop folder and tells Python where to find your scripts.

```python
# --- Step 1: Set up the Environment ---
from pathlib import Path
import sys

# !!! IMPORTANT: YOU MUST EDIT THIS LINE !!!
# Change the path below to the location where you extracted the workshop files.
# Windows example: project_root = Path('C:/Users/YourUser/FOSS4G_Workshop')
# macOS/Linux example: project_root = Path('/home/user/foss4g_workshop')
project_root = Path('YOUR_WORKSHOP_FOLDER_PATH_HERE')

if not (project_root / 'scripts').exists():
    raise FileNotFoundError(f"Could not find the 'scripts' subfolder. Did you launch QGIS from the correct directory? Current Path: {project_root}")

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

1. **Load Data**: Check that the `clipped_residential_properties.gpkg` and `clipped_gpmainsites.gpkg` files are present in the Table of Contents in QGIS. If not, add these manually from the package.
2. **Select Origins**: Select the `clipped_gpmainsites` layer in the Layers Panel. Make sure the layer is clicked/highlighted in the Table of Contents.
3. **Run Code**:

```python
# --- Step 4.1: Load Origin Layer ---
origins = active_layer_to_gdf()
```

4. **Select Destinations**: Select the `clipped_residential_properties` layer in the Layers Panel. Make sure this other layer is clicked/highlighted in the Table of Contents and the Origins are no longer clicked/highlighted.
5. **Run Code**:

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

The `travel_time_results.qml` file can be used to quickly apply a style to the results layer. The travel_time_results.qml file can be used to quickly apply a style to the results layer. To apply this, right click on the outbound_accessibility_results layer > Properties > Symbology > Style > Load Style > File > Add file > Add the `travel_time_results.qml file` > Load

---

## Exploring Further (Optional Tasks)

For those who finish early, here are some extra tasks to explore more capabilities of `r5py`.

### Task 1: Tweaking the Analysis Parameters

The core of the analysis happens in the `get_travel_time_matrix` function.

1. In the QGIS Browser panel, navigate to your project folder, then into the `scripts` subfolder.
2. Drag the `travel_time_analysis.py` file into the QGIS Python Editor window.
3. Try changing some of the parameters inside the `r5py.TravelTimeMatrix` call (e.g., `max_time`, `departure_time`, `speed_walking`). For full details on the parameters available, see the [r5py docs](https://r5py.readthedocs.io/stable/reference/reference.html#r5py.TravelTimeMatrix)
4. Click the "Run Script" button in the editor to save the changes to memory.
5. Now, re-run Step 5 from the main workshop guide above to see how your results change.

### Task 2: Calculate Inbound Journeys

Our main analysis was "outbound". Let's calculate the "inbound" journey time from reachable destinations back to our origins. This is a more efficient approach for large datasets as we only calculate return journeys for destinations we know we can get to.

Run the following code block in the QGIS Python Editor.

```python
# --- Task 2: Inbound Journey Analysis ---
print("\n--- Starting Inbound Analysis ---")

# First, find which destinations were reachable from our outbound analysis
inbound_origins = results_gdf[results_gdf['travel_time'] < 90]
print(f"Found {len(inbound_origins)} reachable destinations to use as inbound origins.")

# Copy original origins as inbound_destinations, to avoid confusion
inbound_destinations = origins.copy()

# Now, calculate inbound travel times, swapping origins and destinations
# The reachable destinations are now the origins.
# The original origins are now the destinations.
inbound_tt_df = get_travel_time_matrix(transport_network, inbound_origins, inbound_destinations)

# For each residential property (from_id), find the quickest journey
shortest_inbound_tt = inbound_tt_df.sort_values("travel_time").drop_duplicates("from_id")

# Rename columns for clarity before merging
shortest_inbound_tt = shortest_inbound_tt.rename(columns={
    "travel_time": "inbound_travel_time",
    "from_id": "inbound_from_id",
    "to_id": "inbound_to_id"
})

# Merge the quickest return journey time back to the original origins layer
inbound_results_gdf = inbound_origins.merge(
    shortest_inbound_tt[["inbound_travel_time", "inbound_from_id", "inbound_to_id"]],
    left_on="id",
    right_on="inbound_from_id",
    how="left"
).drop(columns=["id", "from_id"])

# Handle cases where no return journey was found
inbound_results_gdf['inbound_travel_time'] = inbound_results_gdf['inbound_travel_time'].fillna(90)

# Add the results to QGIS. This layer will have a point for every residential property.
add_gdf_to_qgis(inbound_results_gdf, "inbound_accessibility_results")

print("\n--- Inbound Analysis Complete ---")
print("A new 'inbound_accessibility_results' layer has been added.")
```

### Task 3: Get a Detailed Point-to-Point Itinerary

Let's find the specific turn-by-turn route between one origin and one destination using the results we just generated.

1. Open the attribute table for the **`outbound_accessibility_results`** layer in QGIS.
2. Find an interesting row (one with a `travel_time` less than 90). Note down the value from the **`from_id`** column (this is your origin) and the **`id`** column (this is your destination).
3. Copy the code below into the QGIS editor.
4. **Replace the placeholder `0` values** with the `from_id` and `id` numbers you found.
5. Run the script.

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
