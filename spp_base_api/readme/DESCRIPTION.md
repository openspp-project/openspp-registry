# OpenSPP Base API

## Overview

The [spp_base_api](spp_base_api) module provides foundational API functions and methods for interacting with the OpenSPP system. It acts as a bridge between the core OpenSPP functionalities and external systems, enabling data exchange via APIs or XML-RPC. This module does not introduce any user-facing features but serves as a building block for other modules that require API access to OpenSPP data.

## Purpose

The main purpose of this module is to:

- Establish a standardized way to access and manipulate OpenSPP data externally.
- Provide a consistent and reusable API framework for other OpenSPP modules.
- Enable seamless integration with external applications and systems.

## Functionality

The [spp_base_api](spp_base_api) module introduces several key functions and methods to the Odoo models, extending their capabilities for API interaction:

- **search_or_create**:  Searches for a record based on given values. If no match is found, it creates a new record with the provided values.
- **search_read_nested**:  Performs a nested search across related models and returns a list of dictionaries representing the results. This allows retrieving data from multiple linked models in a single API call.
- **create_or_update_by_external_id**: Creates or updates records based on an external ID. This is crucial for synchronizing data with external systems that rely on unique identifiers.

## Integration with other modules

The [spp_base_api](spp_base_api) module is designed to be a dependency for other modules that need API access. For instance, a hypothetical module [spp_external_integration](spp_external_integration) could depend on [spp_base_api](spp_base_api) module is designed to be a dependency for other modules that need API access. For instance, a hypothetical module `spp_external_integration` could depend on `spp_base_api` and utilize its functions to:

1. Fetch data from OpenSPP through defined API endpoints.
2. Create or update records in OpenSPP based on data received from external systems.
3. Ensure data consistency between OpenSPP and other integrated applications.

By providing these base functionalities, the [spp_base_api](spp_base_api) module streamlines the development of other OpenSPP modules that interact with external systems and APIs. 
