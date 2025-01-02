# OpenSPP Change Request: Create Group

## Overview

The [spp_change_request_create_farm](spp_change_request_create_farm) module extends the OpenSPP Change Request system to specifically handle requests for adding new Farm within the registry. It leverages the framework provided by the [spp_change_request](spp_change_request) module and integrates with other registry modules to streamline the process of adding farmers while maintaining data integrity and consistency.

## Purpose

* **Specialized Change Request Type**: Introduce a dedicated change request type for adding farmers, distinct from other types of registrant modifications.
* **Streamlined Data Collection**:  Provide a tailored form for capturing essential information about the new farmer, including personal details, farmer-specific attributes, and desired group membership details.
* **Group Membership Management**:  Integrate with the [g2p_registry_membership](g2p_registry_membership) module to seamlessly add the new farmer to the specified group upon approval.
* **Enhanced Validation**: Implement specific validation rules relevant to adding farmers, ensuring the accuracy and completeness of the submitted information.

## Module Integration

## Dependencies

The module relies heavily on the following modules:

* **[spp_change_request](spp_change_request)**: Inherits the core change request functionality, including the request workflow, validation processes, approval mechanisms, and integration with the Document Management System ([spp_dms](spp_dms)).
* **[g2p_registry_membership](g2p_registry_membership)**: Integrates with the membership management system to create the appropriate group membership record for the new farmer upon change request approval.
* **[phone_validation](phone_validation)**: Utilizes the phone validation module to ensure phone number entries for the new farmer adhere to correct formatting.
* **[g2p_registry_group](g2p_registry_group)**:  Accesses group information and functionality to display details about the target group for the new farmer.
* **[g2p_registry_individual](g2p_registry_individual)**: Leverages individual registrant management features, inheriting from the individual registrant model.
* **[spp_service_points](spp_service_points)**:  Integrates with service points, allowing change requests to be initiated and managed through designated service points.

## Additional Functionality

* **Custom Change Request Model**:  Introduces the `spp.change.request.create.farm` model, inheriting from the base `spp.change.request` model and adding fields specific to adding farmers, such as farmer-specific details and group membership information.
* **Tailored Forms**: Provides specialized views for creating, displaying, and validating `Create Farm` change requests, including a dedicated form (`view_change_request_create_farm_form`) with relevant fields and a validation-focused form (`view_change_request_create_farm_validation_form`).
* **Automated Individual and Membership Creation**: Upon validation and approval of the change request, the module automatically creates:
    * A new individual registrant record (`res.partner`) for the Individual, populating it with the submitted data.
    * A corresponding group membership record (`g2p.group.membership`), linking the newly created Individual to the designated group.
* **Enhanced User Interface**: Adds specific menu items and actions to the OpenSPP interface, allowing users to efficiently manage `Create Group` requests.

## Conclusion

The [spp_change_request_create_group](spp_change_request_create_farm) module provides a robust and specialized workflow for adding new Farm within the OpenSPP registry. By seamlessly integrating with core change management and registry modules, it ensures data accuracy, consistency, and a streamlined user experience for managing farmer additions.
