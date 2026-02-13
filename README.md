# Extended Hydrofabric: Reproducible Workflows for Water Management Modeling

This repository contains the full set of Jupyter notebooks, workflows, and scripts used to generate the **Extended Hydrofabric** and the associated **relational database** for the Upper Colorado River Basin (UCRB). These workflows enable automated integration of reservoir operations, diversion points, water rights metadata, and other water-management information directly into the national reference hydrofabric framework.


## Overview

Large-scale Water Management Models (WMMs) require standardized, model-ready data describing:

- Reservoir operations  
- Diversion points  
- Water rights and administrative metadata  
- Streamflow gages  
- Hydrologic network topology  

The **Extended Hydrofabric** expands the reference hydrofabric by adding these missing water-management elements, linking all features to persistent `comid` identifiers for plug-and-play use with hydrologic models (e.g., NHM, NWM) and WMMs (e.g., MODSIM, PyWR).


### Included
- Jupyter notebooks demonstrating:
  - Automated extension of the hydrofabric  
  - Construction and population of the relational database  
  - Querying and exporting model-ready features for WMM setup


- Database schema diagrams and documentation

### Not Included (User Must Download)
❗ **Raw source datasets** — see the “Required Datasets” section below.

---


## 📂 Repository Structure

````
├── data
│   ├── Diversions
│   ├── GageLoc
│   ├── output
│   ├── reference fabric gpkg
│   ├── reservoirs
│   ├── USGS (Lopez) Demands
│   ├── wade data
│   └── wbd
├── Documentation
│   └── Documentation.pdf
├── examples
│   ├── aggregated_diversions_example.csv
│   ├── PODs.ipynb
│   ├── reservoirs.ipynb
│   └── usgs_gages.ipynb
├── data_quality
│   ├── data_anomalies_log.csv
│   ├── README.md
├── extended_hydrofabric.ipynb
├── extended_hydrofabric_functions.py
├── README.md
├── requirements.in
├── requirements.txt
└── relational_database.ipynb
````

## 📥 Required External Datasets

Before running any notebook, **users must download the raw datasets** and place them into the data folder.

Box Folder: https://usu.box.com/s/uxk5avw54hcrikyjpwpopl3z6whhzg7i

USGS Reference Hydrofabric Version: v1.4

## ▶️ Getting Started

### 1. Add raw datasets into the `data/` directory
Follow the directory layout above.

### 2. Environment Setup
Tested with Python 3.12.3

Create and activate a virtual environment:

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

### 3. Run notebooks in this order

⚠️ Notebooks must be run from the repository root directory so that local modules are correctly resolved.


1. **extended_hydrofabric.ipynb**  
   - Builds reservoir & POD layers  
   - Assigns GNIS/name/stream-order fallbacks  
   - Creates Extended Hydrofabric GeoPackage  
   - Links everything to reference hydrofabric `comid` 

2. **relational_database.ipynb**  
   - Builds schema  
   - Populates reservoir time series, diversion data, water rights  
    

3. **query_examples.ipynb**  
   - Demonstration of querying  
   - Exporting model-ready WMM components 


## 🗄️ Outputs

### 1. Extended Hydrofabric GeoPackage
Includes:
- Full reference hydrofabric (unchanged)  
- Added layers:
  - `reservoir_points`
  - `diversion_points`
- All features linked to flow network via `SOURCE_COMID`

### 2. Relational Database (SQLite)
Contains:
- POI tables  
- Water rights tables  
- Reservoir daily storage/outflow/inflow  
- Diversion time series  


## 📧 Contact

**Ehsan Ebrahimi**  
Utah Water Research Laboratory  
Utah State University  
Email: ehsan.ebrahimi@usu.edu