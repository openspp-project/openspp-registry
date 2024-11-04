# Module: g2p_connect_demo

## Overview

The `g2p_connect_demo` module serves as a demonstration and testing ground for the OpenSPP system, particularly showcasing the capabilities of the G2P Connect system. This module is not intended for production use but rather for development, testing, and demonstration purposes.

## Purpose

The primary purpose of `g2p_connect_demo` is to:

- **Generate Sample Data:** Provide a mechanism to create realistic but anonymized sample data for registries, individuals, groups, and change requests. This data can be used to populate the OpenSPP system for testing, training, and demonstration purposes.
- **Showcase System Functionality:** Demonstrate the integration and interaction between different OpenSPP modules in a realistic scenario. This includes modules related to registry management ([g2p_registry_base](g2p_registry_base)), individual and group registration ([g2p_registry_individual](g2p_registry_individual), [g2p_registry_group](g2p_registry_group), [g2p_registry_membership](g2p_registry_membership)), programs ([g2p_programs](g2p_programs)), and custom fields ([spp_custom_field](spp_custom_field)).
- **Facilitate Testing and Development:** Provide a controlled environment with pre-populated data to facilitate the testing and development of new features and modifications to the OpenSPP system.

## Key Features

- Generates a configurable number of groups and individuals with realistic demographic data.
- Creates various relationships between individuals within groups, simulating households or families.
- Populates custom fields with relevant data to illustrate the flexibility of the system.
- Includes functionalities to generate change requests, mimicking real-world scenarios like adding children to a household.

## Integration with other modules

`g2p_connect_demo` builds upon the foundation laid by several other OpenSPP modules:

- **[spp_base_demo](spp_base_demo):** Utilizes the base demo module for generating localized sample data.
- **Registry Modules:** Leverages the functionality of [g2p_registry_base](g2p_registry_base), [g2p_registry_individual](g2p_registry_individual), [g2p_registry_group](g2p_registry_group), and [g2p_registry_membership](g2p_registry_membership) to create and manage individuals, groups, and their relationships.
- **[g2p_programs](g2p_programs):** Integrates with program definitions to simulate the enrollment of generated individuals and groups into social protection programs.
- **[spp_custom_field](spp_custom_field):** Utilizes the custom field framework to demonstrate how additional data points can be captured and managed within the registry.

## Usage

The `g2p_connect_demo` module is primarily intended for developers and implementers working with the OpenSPP system. 

By using the provided interface, users can generate a specified number of groups and individuals. The module takes care of creating realistic relationships, assigning custom field values, and populating other relevant data.

## Disclaimer

It is important to reiterate that this module is for **demonstration and development purposes only**. The generated data, while designed to appear realistic, should not be used in a production environment or for any real-world social protection programs. 
