# Context: Data Sources and Production Methodology

This document provides additional context on the data sources used for this workshop and how the methodology was scaled up for a real-world national analysis project.

---

## Data Sources

The datasets used in this workshop are clipped subsets of larger, national datasets. Here is a summary of the original sources and processing steps:

- **GP Surgeries (Destinations):** The destination points for GP practices were downloaded from **DataMapWales**.
  - Link: [https://datamap.gov.wales/layergroups/geonode:gp_sites_ogl](https://datamap.gov.wales/layergroups/geonode:gp_sites_ogl)

- **Residential Properties (Origins):** The origin points were derived from a national residential property dataset. To make the analysis computationally feasible, the ~1.5 million individual properties were consolidated into ~140,000 network-snapped cluster points. Each cluster represents properties no more than 75 metres (approximately a one-minute walk) from each other along the transport network. This dramatically speeds up analysis while maintaining a high level of geographic accuracy.

- **Bus Timetable Data (GTFS):** Timetable data for bus services was downloaded in the standard GTFS format from the UK Government's **Bus Open Data Service (BODS)**.
  - Link: [https://data.bus-data.dft.gov.uk/timetable/download/](https://data.bus-data.dft.gov.uk/timetable/download/)
  - The national dataset was then clipped to the study area using the **UK2GTFS** tool.
  - Link: [https://itsleeds.github.io/UK2GTFS/](https://itsleeds.github.io/UK2GTFS/)

- **Train Timetable Data (GTFS):** Train data was downloaded from **Network Rail** in the CIF (Common Interface File) format.
  - Link: [https://wiki.openraildata.com/index.php?title=SCHEDULE](https://wiki.openraildata.com/index.php?title=SCHEDULE)
  - This was converted from CIF to GTFS using the `nr2gtfs` function in the **UK2GTFS** tool.
  - *Note: Other CIF downloads from the Rail Delivery Group (RDG) could not be successfully converted with the `atoc2gtfs` function at the time of analysis.*

- **OpenStreetMap (OSM) Data:** The underlying road and path network was downloaded from **Geofabrik**.
  - Link: [https://www.geofabrik.de/data/download.html](https://www.geofabrik.de/data/download.html)
  - The data for Great Britain was clipped to the study area using **osmconvert**.
  - Link: [https://wiki.openstreetmap.org/wiki/Osmconvert](https://wiki.openstreetmap.org/wiki/Osmconvert)

---

## Use in Production: The Welsh Index of Multiple Deprivation (WIMD)

The methodology demonstrated in this workshop was successfully scaled up to perform a national accessibility analysis for the **Welsh Index of Multiple Deprivation (WIMD) - Access to Services Domain**. This involved calculating travel times to eight different service types across the whole of Wales.

### Key Methodological Points:

- **Realistic Travel Times:** The `departure_time_window` parameter in `r5py` was crucial. By setting a window of one or two hours, we could calculate trips departing every minute within that window. The analysis then returned the **50th percentile (median)** travel time. This provides a much more realistic and robust measure of accessibility than a single, best-case journey time.

- **Computational Efficiency:** The "outbound-first" approach was key to making the analysis manageable.
    1. First, the **outbound** leg (from a relatively small number of origins to all ~140k destinations) was calculated, which is computationally fast.
    2. Then, only the destinations that were **reachable** within the 90-minute cutoff were used as the origins for the **inbound** leg.
    3. This reduced the number of calculations needed for the return journey, significantly cutting down on total analysis time.

- **Scaling with Multiprocessing:** To run the analysis at a national scale, Python's `multiprocessing` library was used to divide the list of origins among 32 parallel processes on a high-performance machine. This allowed a complete round-trip analysis for a single service type to be completed in approximately **40 minutes**.