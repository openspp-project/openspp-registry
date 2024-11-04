# OpenSPP Land Record 

## Overview

The **OpenSPP: Land Record** module extends OpenSPP's capabilities to manage and visualize land records. Building upon the [G2P Registry: Base](G2P Registry: Base) and [OpenSPP Base GIS](G2P Registry: Base](OpenSPP Base GIS](G2P Registry: Base) and [OpenSPP Base GIS) modules, it provides a framework for recording land parcels, ownership details, lease agreements, and visualizing these records geospatially. 

## Purpose

This module is designed to:

* Record essential details of land parcels, including size, coordinates, and usage.
* Link land parcels to specific farms and registrants in the OpenSPP system.
* Track land ownership and lease arrangements.
* Visualize land records on maps, leveraging the GIS capabilities of OpenSPP. 

## Functionality and Integration

**OpenSPP: Land Record** extends existing modules with the following features:

1. **Land Record Model (`spp.land.record`):**  This core model stores information about each land parcel, including:

    * **Link to Farm:** Connects the land record to a specific farm (`res.partner`) in the system.
    * **Parcel Details:** Records the parcel's name/ID, acreage, coordinates (point and polygon), and land use type.
    * **Ownership and Lease:**  Links to owner and lessee records (using `res.partner`), along with lease start and end dates. 

2. **Integration with [G2P Registry Base](G2P Registry Base):**  

    * Leverages the `res.partner` model from [G2P Registry Base](G2P Registry Base) to link land records with existing farms, owners, and lessees.
    * Benefits from the robust identification, relationship management, and tagging features provided by [G2P Registry Base](G2P Registry Base). 

3. **Geospatial Visualization:**

    * Integrates with the [OpenSPP Base GIS](OpenSPP Base GIS) module to visualize land records on maps.
    * Provides a `get_geojson` method to generate GeoJSON representations of land records, enabling their display as data layers on maps.
    * Allows users to visualize land parcels, ownership boundaries, and other land-related information in a spatial context.

## Example Use Cases:

* **Land Tenure Mapping:**  Visualize landholding patterns within a region, identifying potential issues related to land fragmentation, insecure tenure, or land disputes.
* **Program Targeting:** Design targeted interventions by identifying farmers or beneficiaries based on land use, size of holdings, or ownership status.
* **Monitoring Land Use Change:** Track changes in land use over time (e.g., conversion of forest to agricultural land), supporting environmental monitoring and sustainable land management initiatives.

## Conclusion

The **OpenSPP: Land Record** module enhances OpenSPP's capacity to manage and analyze land-related data.  By integrating with core registry and GIS functionalities, it provides a valuable tool for policymakers, program implementers, and researchers working on land governance, agricultural development, and social protection in the context of low- and middle-income countries. 
