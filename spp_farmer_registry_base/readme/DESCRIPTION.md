# OpenSPP Farmer Registry Base

## Overview

The `spp_farmer_registry_base` module serves as the foundation for managing farmer registries within the OpenSPP system. It builds upon several core OpenSPP modules to provide functionalities specific to farmer registration and farm data management. 

## Purpose

This module aims to:

* Extend the generic registry features to capture data relevant to farmers and their agricultural practices.
* Model the relationships between farmers, farms, land parcels, and agricultural activities.
* Integrate with GIS capabilities to visualize farm locations and land boundaries.

## Module Dependencies and Integration

1. [g2p_registry_membership](g2p_registry_membership): Used to manage memberships between individual registrants and groups.
2. [spp_base_gis](spp_base_gis): Provides the foundation for visualizing and interacting with geospatial data.
3. [spp_land_record](spp_land_record): Enables managing and visualizing land records, linking them to farms and registrants.
4. [g2p_registry_base](g2p_registry_base): Provides the basic structure for managing registrant data, relationships, and identification.
5. [g2p_registry_group](g2p_registry_group): Extends the base registry to handle groups of registrants, such as farmer cooperatives.
6. [g2p_registry_individual](g2p_registry_individual): Extends the base registry with functionalities for managing individual registrant data.

## Functionality and Integration Details

## Farmer Information

* Extends the `res.partner` model (from [g2p_registry_base](g2p_registry_base)) to include farmer-specific details like years of experience, formal agricultural training, household size, etc.
* Introduces a temporary model `spp.farmer` to store farmer-specific information that can be later transferred to the main `res.partner` model, ensuring data consistency.
* Integrates with [g2p_registry_individual](g2p_registry_individual) to leverage existing features for managing individual registrant profiles.

## Farm Management

* Introduces the `Farm` model (inheriting from `res.partner`) to represent individual farms.
* Links farms to land records using the `spp.land.record` model, enabling the tracking of land parcels associated with each farm.
* Allows recording details about farm types, sizes, legal status, and other relevant information.

## Agricultural Activities

* Introduces the `spp.farm.activity` model to record information about agricultural activities undertaken on each farm.
* Captures data on crop cultivation, livestock rearing, and aquaculture practices.
* Links activities to specific land parcels using the `spp.land.record` model, providing a granular view of land use within a farm.

## Farm Assets and Inputs

* Introduces models for managing farm assets (`spp.farm.asset`) and inputs like fertilizers (`spp.fertilizer`), chemicals (`spp.farm.chemical`), and feed items (`spp.feed.items`).
* Allows associating these assets and inputs with specific farms and, optionally, to specific land parcels within a farm.

## GIS Integration

* Leverages the [spp_base_gis](spp_base_gis) module to enable visualization of farm locations and land boundaries on a map.
* Provides a dedicated GIS view for `res.partner` to display farms and their associated land parcels.
* Utilizes GeoJSON representations of land records from [spp_land_record](spp_land_record) to display farm boundaries as data layers on the map.

## Additional Features

* **Extension Services:** Records details about extension services provided to farmers, linked to specific farms and optionally to specific land parcels.
* **Species Information:**  Includes a dedicated model (`spp.farm.species`) for managing information about crop, livestock, and aquaculture species relevant to the registry. 

## Conclusion

The `spp_farmer_registry_base` module, through its integration with various other OpenSPP modules, provides a comprehensive system for creating and managing detailed farmer registries.  It not only facilitates the collection of essential farmer and farm data but also enables spatial analysis and visualization, making it a powerful tool for agricultural development programs and initiatives. 
