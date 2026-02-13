# Data Anomalies Log

This directory contains a structured anomaly log for the **Extended Hydrofabric** data product.

The file `data_anomalies_log.csv` documents record-level irregularities identified during integration of diversion points and related water management features into the Extended Hydrofabric framework.

This log supports transparency, traceability, and reproducibility of the data integration workflow.

---

## Scope

- Each row represents a specific feature-level anomaly.
- The log reflects issues identified to date and is not intended to represent a complete validation of all records.
- Entries are retained for auditability and should not be deleted after correction. If resolved, documentation should reflect the change in future versions.

---

## File Description

### `data_anomalies_log.csv`

This file documents known data anomalies detected during processing or manual review.

### Column Definitions

- **No.**  
  Sequential identifier for anomaly tracking within the log.

- **Layer**  
  The dataset layer in which the anomaly occurs (e.g., DIVERSION_POINTS).

- **fid**  
  Feature ID from the source geospatial layer.

- **ID**  
  Internal identifier associated with the feature in the Extended Hydrofabric workflow.

- **POI_NATIVE_ID**  
  Native point-of-interest identifier reported by the original data source.

- **SOURCE_COMID**  
  The assigned reference hydrofabric COMID corresponding to the feature’s hydrologic connection.

- **Issue_Category**  
  Classification of the anomaly (e.g., incorrect COMID assignment, mismatch in water source, spatial snapping issue, etc.).

- **Hydrologically Correct**  
  Indicates whether the current `SOURCE_COMID` assignment is hydrologically correct after review (e.g., Yes/No or True/False).

- **Description**  
  Detailed explanation of the anomaly and context for review or correction.

---

## Intended Use

This anomaly log is provided to:

- Document feature-level inconsistencies
- Support reproducibility of hydrologic network linkage
- Facilitate quality assurance and future corrections
- Increase transparency in large-scale water management data integration

Users applying the Extended Hydrofabric for modeling workflows should consult this log when interpreting diversion-to-network linkages.

---

## Versioning

- The anomaly log is version-controlled within the GitHub repository.
- Each tagged release includes a snapshot of this file corresponding to that version.
- Updates to anomalies should be tracked through repository commits and release tagging.

---
