# OpenSPP Service Points

This document outlines the **OpenSPP Service Points** module, which adds functionality to manage service points and their agents within the OpenSPP ecosystem. It enables the registration and tracking of service points, their associated areas, offered services, and their connection to company entities and their respective contacts.

## Purpose

The **OpenSPP Service Points** module is designed to:

* **Manage Service Point Information**: Store and manage details about each service point, including their name, location, contact information, and operational status.
* **Associate Service Points with Areas**: Link service points to specific geographical areas defined in the [spp_area](spp_area) module, enabling location-based management and reporting.
* **Define and Assign Service Types**:  Categorize service points based on the types of services they provide, facilitating targeted program delivery and monitoring.
* **Connect with Company Entities**: Establish a relationship between service points and formal company entities within the system.
* **Manage User Accounts for Contacts**: Facilitate the creation and management of user accounts for individuals associated with the company linked to a service point.

## Dependencies and Integration

1. **G2P Registry: Base ([g2p_registry_base](g2p_registry_base))**: Leverages the core registrant management features provided by the **G2P Registry: Base** module.  This includes the use of the `res.partner` model to represent both companies and individuals associated with service points.

2. **OpenSPP Area ([spp_area](spp_area))**: Integrates with the **OpenSPP Area** module to associate service points with specific geographic areas.  The `area_id` field on the `spp.service.point` model links a service point to an area defined in the **OpenSPP Area** module.

3. **Phone Validation (phone_validation)**: Utilizes the **Phone Validation** module to ensure phone numbers associated with service points are properly formatted and validated.

4. **Auth Signup (auth_signup)**: Integrates with the **Auth Signup** module to streamline the creation of user accounts for contacts associated with companies linked to service points.

## Additional Functionality

* **Service Point Management (spp.service.point)**: 
    * Introduces a dedicated model (`spp.service.point`) for storing and managing service point data.
    * Tracks service point operational status (active/disabled) and maintains a history of status changes.
    * Provides functionality to disable and enable service points, recording reasons for disabling. 

* **Service Type Definition (spp.service.type)**:
    * Includes a model (`spp.service.type`) for defining and managing different categories of services offered by service points.

* **User Account Creation**:
    * Offers a streamlined process to automatically create user accounts for contacts associated with the company linked to a service point.
    * Assigns appropriate security groups to newly created users to manage access permissions.

## Conclusion

The **OpenSPP Service Points** module streamlines the management of service points and their agents within the OpenSPP system. It provides a structured approach to track service point details, connect them to geographical locations and company entities, and manage user accounts for individuals involved in service delivery. This contributes to a more organized and efficient operation of social protection programs and farmer registries. 
