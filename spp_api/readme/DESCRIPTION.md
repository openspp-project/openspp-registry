# OpenSPP API

## Overview

The [spp_api](spp_api) module provides a comprehensive framework for building and managing a RESTful API for the OpenSPP platform. It builds upon the foundation laid by the [spp_base_api](spp_base_api) module, adding crucial components for API definition, documentation, and security. 

## Purpose

This module is designed to:

- **Define API Endpoints:** Create, configure, and manage API endpoints for accessing and manipulating data within the OpenSPP system.
- **Generate API Documentation:** Automatically generate OpenAPI (Swagger) documentation for all defined API endpoints, providing a clear and interactive interface for developers.
- **Enforce API Security:** Integrate with the [spp_oauth](spp_oauth) module to handle authentication and authorization for API requests, ensuring secure access to sensitive data.
- **Log API Interactions:** Record details of all incoming API requests and outgoing responses, facilitating debugging, monitoring, and auditing.

## Dependencies

- **[spp_base_api](spp_base_api):** This module relies on [spp_base_api](spp_base_api) for its core API interaction functions and methods.
- **web:** Leverages Odoo's web framework for routing and handling HTTP requests.
- **[spp_oauth](spp_oauth):** Integrates with the [spp_oauth](spp_oauth) module to implement OAuth 2.0-based authentication and authorization for securing API access.

## Functionality and Integration

The [spp_api](spp_api) module introduces key components for building a robust API:

**1. API Namespaces and Paths:**

- **Namespaces:**  Represent logical groupings of API endpoints, often associated with specific functionalities or versions (e.g., `v1`, `v2`).
- **Paths:** Define individual API endpoints within a namespace, specifying the HTTP method (GET, POST, PUT, DELETE, PATCH), URL path, data model, fields to expose, and any filtering or domain logic.

**2. API Documentation:**

- **OpenAPI (Swagger) Generation:** The module automatically generates OpenAPI documentation based on the defined namespaces and paths. This documentation serves as a comprehensive guide for developers, detailing available endpoints, request/response formats, and authentication requirements.

**3. API Security:**

- **OAuth 2.0 Integration:**  Seamlessly integrates with [spp_oauth](spp_oauth) to enforce authentication and authorization using OAuth 2.0 standards. API requests must include valid access tokens, obtained through the OAuth 2.0 flow. 

**4. API Logging:**

- **Detailed Logs:**  Records comprehensive logs for all API interactions, including the request method, URL, parameters, data, response status code, and response data.
- **Configurable Logging Levels:**  Allows administrators to configure the level of detail logged for requests and responses (e.g., disabled, short, full debug).

**5. Integration with Other Modules:**

- Any OpenSPP module that wants to expose data or functionalities through an API can leverage the [spp_api](spp_api) module.
- Modules define their API endpoints using namespaces and paths, ensuring consistency and automatic documentation generation.
- The [spp_api](spp_api) module handles routing, authentication, and logging for these endpoints, simplifying development and ensuring API security.

## Conclusion

The [spp_api](spp_api) module is the cornerstone for building and managing a secure and well-documented RESTful API for the OpenSPP platform. It provides a standardized framework for API development, streamlines integration with other modules, and enhances the security of OpenSPP data by leveraging OAuth 2.0 authentication. 
