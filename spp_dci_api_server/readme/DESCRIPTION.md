# OpenSPP DCI API Server

## Overview

The [spp_dci_api_server](spp_dci_api_server) module provides a RESTful API that adheres to the DCI (Digital Convergence Initiative) specification within the OpenSPP platform. This API enables authorized external systems to securely interact with OpenSPP's registry data, particularly focusing on individual registrant information.

## Purpose

This module serves as a bridge between OpenSPP and external systems seeking to access and utilize registry data. It facilitates the following:

- **Data Exchange:** Enables secure and standardized data exchange between OpenSPP and DCI-compliant systems.
- **Interoperability:** Promotes interoperability by adhering to the DCI specification, allowing various systems to communicate seamlessly with OpenSPP.
- **Data Access Control:** Enforces strict authentication and authorization mechanisms, ensuring that only authorized systems can access sensitive registry information.

## Dependencies

- [g2p_registry_base](g2p_registry_base): The [spp_dci_api_server](spp_dci_api_server) module relies on the core registry functionality provided by the [g2p_registry_base](g2p_registry_base) module. This includes the management of registrants, their IDs, relationships, and other essential attributes.
- [spp_oauth](spp_oauth): This module leverages the OAuth 2.0 authentication and authorization mechanisms provided by the [spp_oauth](spp_oauth) module. External systems are required to authenticate using OAuth 2.0 before they can access the DCI API endpoints.
- [g2p_registry_individual](g2p_registry_individual): This module utilizes the individual-specific data structures and functionalities provided by the [g2p_registry_individual](g2p_registry_individual) module. This is crucial for retrieving and formatting individual registry data according to the DCI specification.

## Functionality and Integration

The [spp_dci_api_server](spp_dci_api_server) module exposes specific API endpoints for handling DCI-related requests:

1. **Authentication Endpoint (`/oauth2/client/token`)**:  This endpoint, handles the OAuth 2.0 authentication flow. External systems must authenticate using their client credentials to obtain an access token, which is required for accessing protected API endpoints.

2. **DCI Sync Search Endpoint (`/api/v1/registry/sync/search`)**: This endpoint receives search requests from external systems. These requests, formatted according to the DCI specification, include criteria for filtering individual registrants within OpenSPP.  The module processes these requests, retrieves matching registrant data, and returns the results in a standardized DCI response format.

    - **Integration with [g2p_registry_individual](g2p_registry_individual):** The module utilizes the `get_dci_individual_registry_data` method from the [g2p_registry_individual](g2p_registry_individual) module to retrieve and structure individual registry data according to the DCI format.
    - **Data Mapping:**  The module maps DCI attribute names to corresponding fields in the OpenSPP database schema, ensuring accurate data retrieval and formatting.
    - **Error Handling:** The module implements robust error handling, returning appropriate error codes and messages in the DCI response format for any invalid requests or data access issues.

## Conclusion

The [spp_dci_api_server](spp_dci_api_server) module is essential for integrating OpenSPP with external systems that adhere to the DCI specification. By providing secure, standardized API endpoints, the module facilitates efficient data exchange and interoperability while ensuring the privacy and security of sensitive registry information. 
