# OpenSPP Base Demo

This module serves as a demonstration of the GIS capabilities provided by the [OpenSPP Base GIS](OpenSPP Base GIS)(./openspp-base-gis) module. It extends the functionality of the base module by adding practical examples and use cases. 

## Purpose

The [spp_base_gis_demo](spp_base_gis_demo) module aims to:

- Showcase how to integrate GIS features into existing OpenSPP models.
- Provide concrete examples of using GIS views, data layers, and raster layers.
- Offer a starting point for developers to build upon and customize for specific project needs.

## Integration with Other Modules

This module directly interacts with:

- **[spp_base_gis](spp_base_gis)**: It utilizes the core GIS functionality provided by this module, such as GIS views, data layers, and raster layers.
- **contacts**: It extends the `res.partner` model from the `contacts` module to include geographic fields, demonstrating how to add GIS capabilities to existing models. 

## Additional Functionality

The [spp_base_gis_demo](spp_base_gis_demo) module offers:

- **Extended Partner Model:**  The `res.partner` model is enhanced with the following fields:
    - `geo_point`:  Stores the geographic coordinates of a partner as a point.
    - `geo_line`: Stores the geographic coordinates of a partner as a line.
    - `geo_polygon_field`: Stores the geographic coordinates of a partner as a polygon.

- **GIS Views:**  The module defines GIS views for the `res.partner` model, allowing users to visualize partners on a map based on their geographic information. This includes:
    - Point visualization for `geo_point`.
    - Line visualization for `geo_line`.
    - Polygon visualization for `geo_polygon_field`.

- **Data and Raster Layers:** The module configures data layers to represent partners on the map using different geometric representations. It also sets up a raster layer to provide a background map for context.

## Example

The module demonstrates how to visualize the location of a partner (e.g., a beneficiary or a farmer) on a map.  Users can view and interact with the partner data in a geospatial context, gaining insights into their distribution and spatial relationships.

## Conclusion

The [spp_base_gis_demo](spp_base_gis_demo) module serves as a practical guide for implementing GIS features within the OpenSPP ecosystem. It provides tangible examples and building blocks for developers to leverage the power of geospatial data in social protection programs and farmer registries.
