# FOSS4G Workshop: Public Transport Accessibility Analysis in QGIS

**Workshop Overview**

Welcome! This workshop will guide you through performing a public transport accessibility analysis using Python inside QGIS. We will calculate the travel time from a set of origins to a set of destinations using open-source tools and data.

The analysis will be conducted interactively within the QGIS Python Console to help you understand each step of the process.

---

## Prerequisites

Before you begin, you must have the following software:

1.  **QGIS (version 3.28 or newer)**: If you do not have it, download it from [qgis.org](https://qgis.org/en/site/forusers/download.html).
2.  **This GitHub Repository**: You need all the data and script files.

---

## 🚀 Setup Instructions (Crucial!)

This setup ensures QGIS can find the correct Java version and Python packages **without requiring admin rights or permanently changing your system settings**.

### Step 1: Download the Workshop Files

If you haven't already, download this repository as a ZIP file and extract it to a simple, memorable path with **no spaces**, for example: `C:\Users\YourUser\FOSS4G_Workshop\` or `/home/user/foss4g_workshop/`.

### Step 2: Download and Place the Portable JDK (Java 21)

Our analysis library (`r5py`) requires a portable, 64-bit version of JDK 21.

1.  Go to the download page: [**Eclipse Temurin JDK 21 Downloads**](https://adoptium.net/temurin/releases/?version=21)
2.  On the download page, find your Operating System (Windows, macOS, Linux).
3.  Crucially, download the **Archive** file, which will be a `.zip` or `.tar.gz`. **Do NOT download the installer (`.msi` or `.pkg`).** 
4.  Create a new folder named `jdk` inside your main workshop folder.
5.  Extract the contents of the downloaded archive into this new `jdk` folder. Your file structure should now look like this:
    ```
    FOSS4G_Workshop/
    ├── jdk/
    │   └── jdk-21.0.2+13/  <-- (or similar versioned folder)
    │       ├── bin/
    │       ├── conf/
    │       └── ...
    ├── network_data/
    ├── scripts/
    └── ...
    ```

### Step 3: Install Required Python Packages

QGIS comes with its own Python environment. We need to install our required libraries into it. This step also pins the `NumPy` library to an older version to ensure compatibility.

---

#### **For Windows Users**

1.  From the Start Menu, find and open the **"OSGeo4W Shell"**.
2.  In the black terminal window that opens, run the following command. This will install the correct versions of all the required libraries.
    ```batch
    python-qgis-ltr -m pip install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```
3.  Wait for the installation to complete, then you can close the OSGeo4W shell.

---

#### **For macOS and Linux Users**

1.  Open a new standard **Terminal**.
2.  Run the following command. `pip3` is typically linked to the Python installation that QGIS uses.
    ```bash
    pip3 install r5py geopandas JPype1==1.5.0 "numpy<2"
    ```
3.  Wait for the installation to complete.

---

### Step 4: Launch QGIS from a Pre-configured Terminal

This is the most important step for the analysis. We will open a terminal, navigate to our workshop folder, temporarily tell it where to find our portable Java, and then launch QGIS from that same session.

#### **For Windows Users**

1.  **Open a Command Prompt.** Go to the Start Menu and type `cmd`.
2.  **Navigate to your workshop folder.** Use the `cd` command.
    ```batch
    cd C:\Users\YourUser\FOSS4G_Workshop
    ```
3.  **Set the `JAVA_HOME` variable.** This command points to the `jdk` folder you created. It is only active for this specific command prompt window. **Note: The version number in the path below might be slightly different for you.**
    ```batch
    set "JAVA_HOME=%cd%\jdk\jdk-21.0.8+9"
    ```
4.  **Launch QGIS from the same command prompt.** **Note: You may need to adjust the path below to match your QGIS installation version.**
    ```batch
    start "" "C:\Program Files\QGIS 3.40.11\bin\qgis-ltr-bin.exe"
    ```

#### **For macOS and Linux Users**

1.  **Open a new Terminal.**
2.  **Navigate to your workshop folder.** Use the `cd` command.
    ```bash
    cd /home/user/foss4g_workshop
    ```
3.  **Set the `JAVA_HOME` variable.** This command points to the `jdk` folder you created and is only active for this terminal session. **Note: The exact folder name inside `jdk/` may vary slightly.**
    ```bash
    export JAVA_HOME="$PWD/jdk/temurin-21.jdk/Contents/Home"
    ```
4.  **Launch QGIS from the same terminal.**
    * **macOS**:
        ```bash
        open /Applications/QGIS.app
        ```
    * **Linux**:
        ```bash
        qgis
        ```

---

## 💡 Workshop Steps: Interactive Analysis

After completing the setup, launch QGIS from your configured terminal and open the Python Console (**Plugins -> Python Console**). You will now run each of the following code blocks one by one.

### Step 1: Set Up the Environment

This step identifies your workshop folder (because you launched QGIS from there) and tells Python where to find your scripts.

```python
# --- Step 1: Set up the Environment ---
print("--- Step 1: Setting up environment ---")
from pathlib import Path
import sys

# Path.cwd() works here because we launched QGIS from the workshop directory
project_root = Path.cwd()

# This is a good practice check to ensure the path is correct
if not (project_root / 'scripts').exists():
    raise FileNotFoundError(f"Could not find the 'scripts' subfolder. Did you launch QGIS from the correct directory? Current Path: {project_root}")

# Add the scripts folder to Python's path
scripts_path = project_root / 'scripts'
if str(scripts_path) not in sys.path:
    sys.path.append(str(scripts_path))

print(f"Environment is ready. Project root set to: {project_root}")
```

### Step 2: Import Necessary Functions

```python
# --- Step 2: Import Necessary Functions ---
print("\n--- Step 2: Importing tools ---")
import geopandas as gpd
import pandas as pd
from single_core_ttm import single_core_ttm
from workshop_utils import active_layer_to_gdf, add_gdf_to_qgis
print("Tools imported.")
```

### Step 3: Load Origin and Destination Layers

1.  **Load Data**: Add the `clipped_residential_properties.gpkg` and `clipped_gpmainsites.gpkg` files to QGIS from your workshop folder.
2.  **Select Origins**: Select the `clipped_residential_properties` layer in the Layers Panel.
3.  **Run Code**:

```python
# --- Step 3.1: Load Origin Layer ---
print("\n--- Step 3: Loading data ---")
print("ACTION: Loading the selected ORIGINS layer...")
origins = active_layer_to_gdf()
```

4.  **Select Destinations**: Select the `clipped_gpmainsites` layer in the Layers Panel.
5.  **Run Code**:

```python
# --- Step 3.2: Load Destination Layer ---
print("\nACTION: Loading the selected DESTINATIONS layer...")
destinations = active_layer_to_gdf()
```

### Step 4: Run the Travel Time Analysis

```python
# --- Step 4: Run the Travel Time Analysis ---
print("\n--- Step 4: Calculating travel times (this may take a moment)... ---")
travel_time_df = single_core_ttm(origins, destinations)
print("Analysis complete! The result is a table of all possible journey times.")
print("Result preview:")
print(travel_time_df.head())
```

### Step 5: Find the Quickest Route to Each Destination

```python
# --- Step 5: Find the Quickest Route to Each Destination ---
print("\n--- Step 5: Filtering for the quickest route to each destination ---")
shortest_tt = travel_time_df.sort_values("travel_time").drop_duplicates("to_id")
print("Filtering complete.")
print("Result preview:")
print(shortest_tt.head())
```

### Step 6: Join Results Back to Destination Geometries

```python
# --- Step 6: Join Results Back to Destination Geometries ---
print("\n--- Step 6: Joining travel times back to the destination layer ---")
results_gdf = destinations.merge(
    shortest_tt[["travel_time", "to_id"]],
    left_on="id",
    right_on="to_id",
    how="left"
).drop(columns=["to_id"])
print("Join complete.")
```

### Step 7: Handle Unreachable Destinations

After the join, any destination that could not be reached will have a null (`NaN`) value for `travel_time`. For styling purposes, let's replace these nulls with our maximum travel time of 90 minutes.

```python
# --- Step 7: Handle Unreachable Destinations ---
print("\n--- Step 7: Setting travel time for unreachable destinations ---")
results_gdf['travel_time'] = results_gdf['travel_time'].fillna(90)
print("Unreachable destinations handled.")
```

### Step 8: Add the Final Layer to QGIS

The final step! This code will add our GeoDataFrame containing the results as a new layer in your QGIS project, ready for styling and interpretation.

```python
# --- Step 8: Add the Final Layer to QGIS ---
print("\n--- Step 8: Adding results to the QGIS map ---")
add_gdf_to_qgis(results_gdf, "outbound_accessibility_results")
print("\nWorkshop complete! A new layer has been added to your project.")
```

---

## 🗺️ Exploring Further

Congratulations! You've successfully completed the analysis. You can now use QGIS's styling tools to symbolize the `outbound_accessibility_results` layer based on the `travel_time` attribute to create a powerful accessibility map.
