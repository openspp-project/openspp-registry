# OpenSPP Base GIS REST

This module extends the [spp_base_gis](spp_base_gis) by providing RESTful API endpoints for accessing and querying geospatial data. It depends on the following modules:

- **[spp_base_gis](spp_base_gis):**  Provides the core GIS functionalities and data models.
- **[spp_oauth](spp_oauth):**  Enables secure authentication and authorization for API requests using OAuth 2.0.

## Functionality

The `spp_base_gis_rest` module offers a set of RESTful API endpoints that allow external applications and services to:

- **Authenticate and Obtain Access Tokens:**  Utilizes the [spp_oauth](spp_oauth) module to implement OAuth 2.0 flows for secure authentication and token generation.
- **Perform Locational Queries:**  Enables querying geospatial data based on location coordinates (latitude and longitude), layer type (point, line, polygon), and spatial relationships (intersects, within, contains). 
- **Execute Attribute Queries:**  Allows filtering data based on attribute values using operators such as equals, not equals, greater than, etc. 
- **Retrieve Feature Data:** Returns geospatial data in standard formats like GeoJSON, suitable for consumption by GIS clients or other applications.

## Integration with Other Modules

The `spp_base_gis_rest` module seamlessly integrates with:

- **OpenSPP Base GIS:**  It directly leverages the GIS functionalities and data models provided by this module to process queries and return geospatial information.
- **OpenSPP API: Oauth Module:**  It relies on the [spp_oauth](spp_oauth) module for handling API authentication, ensuring that only authorized clients can access the GIS data.

## API Endpoints

The module exposes the following key API endpoints:

- `/v1/gisBB/oauth2/client/token`:  Used by clients to obtain access tokens through OAuth 2.0 flows.
- `/v1/gisBB/query/locationalQuery`:  Performs locational queries based on coordinates and spatial relationships.
- `/v1/gisBB/query/attributeQuery`:  Executes attribute-based queries to filter data. 

## Security

The module inherits its security model from the [spp_oauth](spp_oauth) module. All API endpoints are protected and require valid access tokens for authorization. This ensures that only authorized clients and applications can access and query the geospatial data.

## Conclusion

The `spp_base_gis_rest` module enhances the OpenSPP Base GIS module by providing a secure and standardized way to access and query geospatial data through RESTful API endpoints. This empowers external applications, services, and GIS clients to integrate with OpenSPP and leverage its geospatial capabilities. 
