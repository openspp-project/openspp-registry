# OpenSPP Base 

This document outlines the functionality of the **OpenSPP Base** module, the core module for the OpenSPP system. It builds upon existing G2P Registry modules, providing essential customizations and configurations for OpenSPP's specialized functionalities.

## Purpose

The **OpenSPP Base** module serves as the foundation for other OpenSPP modules, offering:

- **Centralized configurations**:  Provides essential settings and options that apply across the entire OpenSPP system.
- **UI modifications**: Customizes the user interface (UI) to align with OpenSPP's look and feel, enhancing user experience. 
- **Extension points**:  Acts as a base for other modules to inherit and extend functionalities specific to OpenSPP requirements.

## Module Dependencies and Integration

The **OpenSPP Base** module depends on several other modules, integrating their features and extending them for OpenSPP:

- [spp_idqueue](spp_idqueue) : Leverages this module for managing ID card printing requests and workflows.
- [spp_service_points](spp_service_points): Utilizes this module to manage service points and their association with areas, companies, and users. 
- [spp_custom_fields_ui](spp_custom_fields_ui): Depends on this module for a user-friendly interface to manage custom fields for registrants.
- [g2p_registry_membership](g2p_registry_membership):  Integrates with this module to manage memberships between individual registrants and groups.
- [spp_custom_field](spp_custom_field): Extends this module's functionality to add and manage custom fields for registrants, enhancing data collection capabilities.
- [spp_programs](spp_programs):  Integrates with this module for managing both cash and in-kind programs and entitlements. 
- [spp_area](spp_area): Utilizes this module to manage geographical areas and link them to registrants and other relevant data.
- [g2p_registry_base](g2p_registry_base): Inherits core registry functionalities from this module, including registrant management, IDs, relationships, and districts. 
- [g2p_registry_group](g2p_registry_group): Integrates with this module to manage groups of registrants, extending the concept of registrants beyond individuals.
- [utm](utm): Leverages this module for tracking and managing UTM (Urchin Tracking Module) parameters, commonly used in digital marketing campaigns.
- [g2p_registry_individual](g2p_registry_individual): Integrates with this module to manage individual registrant data, including specific attributes and validations.

## Additional Functionality

The **OpenSPP Base** module introduces the following key functionalities:

- **Top-up Card ID Type**: Adds a new ID type specifically for managing "Top-up Cards", including a dedicated field (`card_uid`) for storing the unique 10-character UID of each card.
- **Registrant View Enhancements**: Modifies the registrant views (both individual and group) to include the `card_uid` field, making it accessible for data entry and display.
- **Menu Icon Customization**:  Replaces the default icon for the "Registry" menu item with a custom OpenSPP icon, enhancing visual branding. 
- **Menu Item Hiding**:  Hides specific menu items related to "Link Tracker" and "Discuss" to streamline the OpenSPP user interface and focus on relevant functionalities. 

## Conclusion

The **OpenSPP Base** module acts as the backbone of the OpenSPP system, integrating and extending the functionalities of its dependencies to create a cohesive and tailored platform. Its role in providing central configurations, UI modifications, and extension points makes it essential for the proper functioning and customization of OpenSPP's specialized features. 
