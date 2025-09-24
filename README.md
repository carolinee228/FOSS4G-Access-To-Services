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

This setup ensures QGIS can find the correct Java version **without requiring admin rights or permanently changing your system settings**.

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

### Step 3: Launch QGIS from a Pre-configured Terminal

This is the most important step. We will open a terminal, temporarily tell it where to find our portable Java, and then launch QGIS from that same session.

---

#### **For Windows Users**

1.  **Open a Command Prompt.** Go to the Start Menu and type `cmd`.
2.  **Navigate to your workshop folder.** Use the `cd` command.
    ```batch
    cd C:\Users\YourUser\FOSS4G_Workshop
    ```
3.  **Set the `JAVA_HOME` variable.** This command points to the `jdk` folder you created. It is only active for this specific command prompt window.
    ```batch
    set "JAVA_HOME=%cd%\jdk\jdk-21.0.2+13"
    ```
4.  **Launch QGIS from the same command prompt.** (You may need to adjust the path if your QGIS is installed elsewhere).
    ```batch
    start "" "C:\Program Files\QGIS 3.34.8\bin\qgis-bin.exe"
    ```

---

#### **For macOS and Linux Users**

1.  **Open a new Terminal.**
2.  **Navigate to your workshop folder.** Use the `cd` command.
    ```bash
    cd /home/user/foss4g_workshop
    ```
3.  **Set the `JAVA_HOME` variable.** This command points to the `jdk` folder you created and is only active for this terminal session. Note the folder name inside may vary slightly.
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

This step identifies your workshop folder and tells Python where to find your scripts.

```python
# --- Step 1: Set up the Environment ---
print("--- Step 1: Setting up environment ---")
from pathlib import Path
import sys

# Path.cwd() works here because we launched QGIS from the workshop directory
project_root = Path.cwd()

# This is a good practice check to ensure the path is correct
if not (project_root / 'scripts').exists():
    raise FileNotFoundError(f"Could not find the 'scripts' subfolder. Is the project root correct? Path: {project_root}")

# Add the scripts folder to Python's path
scripts_path = project_root / 'scripts'
if str(scripts_path) not in sys.path:
    sys.path.append(str(scripts_path))

print(f"Environment is ready. Project root set to: {project_root}")
```

### Step 2: Import Necessary Functions
(This step remains the same)
```python
# --- Step 2: Import Necessary Functions ---
print("\n--- Step 2: Importing tools ---")
import geopandas as gpd
from single_core_ttm import single_core_ttm
from workshop_utils import active_layer_to_gdf, add_gdf_to_qgis
print("Tools imported.")
```

### Step 3: Load Origin and Destination Layers
(This step remains the same)
```python
# --- Step 3.1: Load Origin Layer ---
print("\n--- Step 3: Loading data ---")
print("ACTION: Add data to QGIS, then select the ORIGINS layer and run this.")
origins = active_layer_to_gdf()

# --- Step 3.2: Load Destination Layer ---
print("\nACTION: Now select the DESTINATIONS layer and run this.")
destinations = active_layer_to_gdf()
```

### Step 4: Run the Travel Time Analysis
(This step and all subsequent steps remain the same)
```python
# --- Step 4: Run the Travel Time Analysis ---
print("\n--- Step 4: Calculating travel times (this may take a moment)... ---")
travel_time_df = single_core_ttm(origins, destinations)
print("Analysis complete! The result is a table of all possible journey times.")
print("Result preview:")
print(travel_time_df.head())
```

### Step 5: Find the Quickest Route to Each Destination

We are only interested in the *fastest* route to each unique destination.

```python
# --- Step 5: Find the Quickest Route to Each Destination ---
print("\n--- Step 5: Filtering for the quickest route to each destination ---")
shortest_tt = travel_time_df.sort_values("travel_time").drop_duplicates("to_id")
print("Filtering complete.")
print("Result preview:")
print(shortest_tt.head())
```

### Step 6: Join Results Back to Destination Geometries

Let's join our results back to the original destination points so we can visualize them.

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

### Step 7: Add the Final Layer to QGIS

This code will add our results as a new layer in your QGIS project.

```python
# --- Step 7: Add the Final Layer to QGIS ---
print("\n--- Step 7: Adding results to the QGIS map ---")
add_gdf_to_qgis(results_gdf, "outbound_accessibility_results")
print("\nWorkshop complete! A new layer has been added to your project.")
```

---

## 🗺️ Exploring Further

Congratulations! You can now use QGIS's styling tools to symbolize the `outbound_accessibility_results` layer based on the `travel_time` attribute to create a powerful accessibility map.