# OpenSPP Change Request Demo: Add Child/Member

## Overview

The OpenSPP Change Request Demo: Add Child/Member (`spp_change_request_add_children_demo`) module is a demonstration module built on top of the [spp_change_request](spp_change_request) module. This module provides a specific implementation of the change request process, focusing on adding children or new members to an existing group within the registry. This documentation highlights the specific features and functionality of this demo module.

## Purpose

The primary purpose of this module is to showcase a practical implementation of the OpenSPP Change Request framework. It demonstrates how to:

- Create a new change request type specifically for adding children or members to a group.
- Define a tailored form for capturing the necessary information for this type of change.
- Integrate with the ID scanning feature for potential verification of identity.
- Implement data validation rules specific to adding new members.
- Update the registry data upon successful validation and approval of the request.

## Module Dependencies and Integration

The `spp_change_request_add_children_demo` module depends on the following modules:

1. **OpenSPP Change Request ([spp_change_request](spp_change_request))**: This module provides the foundational structure for managing change requests, including workflows, approvals, and data validation. The demo module leverages this existing framework to handle the addition of new members. 

2. **G2P Registry Modules**:  The demo module integrates with various G2P Registry modules to access and update registrant information:
    - **G2P Registry: Base ([g2p_registry_base](g2p_registry_base))**:  Inherits core registrant features and extends them for the specific requirements of the 'Add Children' request.
    - **G2P Registry: Individual ([g2p_registry_individual](g2p_registry_individual))**:  Utilizes this module to create new individual registrant records for the children or members being added.
    - **G2P Registry: Group ([g2p_registry_group](g2p_registry_group))**:  Accesses and updates group registrant information, specifically to add new members to the group.
    - **G2P Registry: Membership ([g2p_registry_membership](g2p_registry_membership))**:  Creates new membership records to establish the relationship between the added individuals and the target group.

3. **[spp_service_points](spp_service_points)**: This module allows for associating change requests, including those for adding children, with specific service points from which they originate.

4. **[phone_validation](phone_validation)**: Ensures that any phone numbers entered during the change request process adhere to valid formats.

## Additional Functionality

- **Dedicated Change Request Type**: The module introduces a new change request type specifically for "Add Children," accessible through a dedicated menu option.
- **Custom Change Request Form**:  A specialized form is implemented to capture information relevant to adding children or members, including their personal details, relationship to the applicant, and supporting documentation.
- **ID Scanner Integration**: The module includes integration with the ID scanning feature, allowing users to scan supporting documents (e.g., birth certificates, IDs) directly into the change request as attachments. 
- **Data Validation**:  Specific validation rules are implemented to ensure the entered data meets the requirements for adding new members. For instance, the module checks for unique identification numbers and valid birthdates. 
- **Automatic Data Update**:  Upon approval of an "Add Children" change request, the module automatically:
    - Creates new individual registrant records for the added children.
    - Establishes membership records to link these individuals to the designated group.

## Example Usage

1. A registrant approaches a service point to add their child to their registered household group.
2. The service point agent initiates an "Add Child/Member" change request through the dedicated menu.
3. The agent fills out the form with the child's information, potentially scanning supporting documents.
4. The change request goes through the defined approval workflow (as configured in the [spp_change_request](spp_change_request) module).
5. Once approved, the module automatically creates a new individual registrant record for the child and adds them as a member to the parent's household group.

## Conclusion

The OpenSPP Change Request Demo: Add Child/Member module serves as a practical example of implementing the change request framework within OpenSPP for a specific use case.  By integrating with various core modules and showcasing features like ID scanning and automatic data updates, it provides a blueprint for developing similar modules for other common change request scenarios. 
