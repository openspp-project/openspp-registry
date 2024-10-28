# OpenSPP Base GIS

## Overview

The OpenSPP Base GIS module enhances the functionality of OpenSPP by adding Geographical Information System (GIS) capabilities. It provides the foundation for visualizing and interacting with geospatial data within the OpenSPP platform. This module depends on the following Odoo modules:

- **contacts:**  Used to manage contact information.
- **web:** Provides the core web framework for building user interfaces.

## Functionality

The Base GIS module introduces several key features:

- **GIS Views:**  Allows the creation of specialized views within OpenSPP models to display geospatial data on interactive maps. These views are defined using the "gis" type in the view definition.

- **Raster Layers:**  Supports the integration of background maps from various sources, including:
    - Distant Web Map Service (WMS)
    - OpenStreetMap
    - Static images

- **Data Layers:**  Enables the visualization of data from OpenSPP models directly on the map. Users can configure:
    - The geometric representation of data (e.g., points, lines, polygons)
    - The field containing the geographic data
    - Styling options such as colors and opacity

- **Spatial Queries:** Provides tools for performing spatial queries to filter data based on geographic relationships such as intersection and distance.

## Integration

The Base GIS module seamlessly integrates with other OpenSPP modules by extending the core functionality with geospatial awareness. For instance:

- **[Registries](Registries)**  The module allows for visualizing registry data on a map. This could include plotting the locations of farmers, beneficiaries, or other entities managed within a registry.
- **[Targeting and Eligibility](Targeting and Eligibility)** GIS data can be incorporated into targeting and eligibility rules. For example, a program might define eligibility based on a beneficiary's location within a specific geographical area.
- **[Monitoring and Evaluation](Monitoring and Evaluation)**  The module facilitates spatial analysis for monitoring and evaluation purposes. Program implementers can visualize program coverage, identify geographic areas with high or low program participation, and track progress over time.

## Configuration

The Base GIS module can be configured through:

- **GIS Views:** Defining GIS views for specific models to control how geospatial data is displayed.
- **Raster Layers:** Adding and configuring background maps from different sources.
- **Data Layers:** Setting up data layers to visualize model data on the map with customized styles.

## Example Use Case

Consider a social protection program where beneficiaries are registered along with their geolocation data. The Base GIS module can be used to:

1.  Create a GIS view for the beneficiary model to display their locations on a map.
2.  Overlay data layers representing program intervention areas to visualize program coverage.
3.  Perform spatial queries to identify beneficiaries residing within or outside specific zones.

This information can be used for program planning, targeting, monitoring, and evaluation.

## Conclusion

The OpenSPP Base GIS module empowers OpenSPP with powerful geospatial capabilities, enabling users to visualize, analyze, and interact with data in new and insightful ways. This strengthens the platform's ability to support effective and efficient social protection programs and farmer registries.
