# OpenSPP Event Data

This document outlines the functionality of the **[spp_event_data](spp_event_data)** module within the OpenSPP ecosystem. This module is designed to record and track specific events related to registrants, building upon the functionalities offered by the base registry modules.

## Purpose

The **[spp_event_data](spp_event_data)** module allows users to associate significant events with both individual and group registrants, enhancing the system's capacity to capture a chronological history of changes and actions. It aims to:

* Provide a structured way to log and store data about events impacting registrants.
* Link these events to the specific data entries they affect, creating a clear audit trail.
* Offer tools to view and navigate the event history of a registrant.

## Module Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)**: This module relies on the foundational structure and functionalities provided by the **[g2p_registry_base](g2p_registry_base](g2p_registry_base](g2p_registry_base)**: This module relies on the foundational structure and functionalities provided by the **[g2p_registry_base)** module, specifically leveraging:
    * **Registrant Data**: Utilizes the core registrant information to associate events with the correct individuals or groups.
2. **[g2p_registry_group](g2p_registry_group)**: Extends its functionality by allowing event data to be linked to group registrants.
3. **Contacts (res.partner)**:  Integrates with the standard Odoo Contacts module, enabling the module to link event data to the respective contact records, enriching the overall profile of the registrant.

## Additional Functionality

* **Event Data Model (spp.event.data)**:
    * Introduces a new data model to store event-specific information.
    * Includes fields to record:
        * Event type (automatically derived from the related data model).
        * Related document/record (using `Many2oneReference` for flexibility).
        * Registrar (person who recorded the event).
        * Collection date and optional expiry date.
        * Status of the event (active/inactive).
* **Automatic Event Type Calculation**:
    * Dynamically determines and displays the event type based on the linked data model, providing a clear and user-friendly representation of the event.
* **Event History on Registrant Forms**:
    * Adds a dedicated tab on both individual and group registrant forms to display their associated event history.
    * Enables users to directly access and review past events related to a specific registrant.
* **Event Creation Wizard**:
    * Provides a streamlined process for creating new event data entries through a dedicated wizard.
    * Simplifies data entry and ensures consistency in event logging.
* **Active Event Management**:
    * Implements logic to manage the active status of events.
    * Automatically ends the previous active event of the same type when a new one is created for the same registrant.
    * Provides a clear view of the current status of events related to a specific data point.

## Conclusion

The **[spp_event_data](spp_event_data)** module enhances OpenSPP by introducing a robust system for tracking and managing significant events throughout the lifecycle of registrants. Its tight integration with core registry modules and the Contacts module ensures that event data is seamlessly incorporated into the platform, enriching data integrity and providing a comprehensive view of registrant history. 
