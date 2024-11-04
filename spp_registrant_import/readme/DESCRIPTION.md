# OpenSPP Registrant Import

This document describes the **OpenSPP Registrant Import** module, which enhances the import functionality within the OpenSPP system, specifically focusing on streamlining the process of importing registrant data. It builds upon the existing import capabilities and introduces features to improve data mapping and ID management.

## Purpose

The **OpenSPP Registrant Import** module aims to:

* **Simplify Data Mapping**: Provide a more intuitive way to map imported data fields to corresponding fields in OpenSPP's registrant models. This reduces the complexity of data preparation and ensures accurate data import.
* **Enhance ID Management**: Introduce a mechanism to generate and assign unique OpenSPP IDs (spp_id) to registrants during the import process. This ensures data integrity and facilitates efficient tracking and management of registrants within the system. 

## Dependencies and Integration

1. **OpenSPP Base** ([spp_base](spp_base)):  Inherits core functionalities from the **OpenSPP Base** module, including access to registrant models and configurations. 

2. **OpenSPP Service Points** ([spp_service_points](spp_service_points)): Leverages the **OpenSPP Service Points** module to associate imported service point data with existing service points in the system using unique IDs. 

3. **OpenSPP Area** ([spp_area](spp_area)): Integrates with the **OpenSPP Area** module to link imported registrant data to specific geographical areas based on unique IDs.

4. **G2P Registry: Group** ([g2p_registry_group](g2p_registry_group)): Works in conjunction with the **G2P Registry: Group** module to facilitate the import of group registrant data and manage group IDs. 

5. **G2P Registry: Individual** ([g2p_registry_individual](g2p_registry_individual)):  Integrates with the **G2P Registry: Individual** module to import individual registrant data and assign individual-specific IDs. 

## Additional Functionality

* **Unique ID Generation and Assignment**: 
    * Automatically generates unique OpenSPP IDs (spp_id) for registrants during import if an ID is not provided in the import file.
    * Adheres to a predefined format for spp_id based on the registrant type (individual, group, service point, area) ensuring consistency.

* **Improved Data Mapping**:
    * Enhances the existing import mapping interface to allow users to directly map columns from their import file to the corresponding fields in OpenSPP's registrant models. 
    * Provides visual cues and validation during the mapping process to minimize errors and ensure accurate data association.

## Conclusion

The **OpenSPP Registrant Import** module streamlines the process of importing registrant data into the OpenSPP system. By simplifying data mapping and automating unique ID generation and assignment, this module enhances data integrity, reduces manual effort, and improves the overall efficiency of data management within OpenSPP. 
