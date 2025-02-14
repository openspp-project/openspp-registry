# OpenSPP Change Request

## Overview

The OpenSPP Change Request ([spp_change_request](spp_change_request)) module streamlines the process of handling changes to registrant information within the OpenSPP system. It provides a structured framework for submitting, reviewing, approving, and applying modifications to existing registrant data.

## Purpose

The module aims to:

* **Formalize Change Requests**: Introduce a standardized procedure for requesting alterations to registrant data, ensuring all changes are documented and tracked.
* **Implement a Multi-Step Approval Process**: Establish a configurable workflow for validating and authorizing change requests, involving different user roles and levels of approval.
* **Maintain Data Integrity**: Safeguard the accuracy and consistency of registrant information by requiring proper justification and authorization for any modifications.
* **Enhance Transparency and Accountability**: Provide a clear audit trail of all change requests, approvals, and applications, promoting transparency and accountability in data management.

## Module Dependencies and Integration

The [spp_change_request](spp_change_request) module leverages and extends the functionality of several other OpenSPP modules:

1. **G2P Registry Modules**: It heavily relies on the G2P Registry modules for accessing and modifying registrant data:
    * **G2P Registry: Base ([g2p_registry_base](g2p_registry_base))**:  Inherits core registrant management features, including the `res.partner` model used to represent registrants.
    * **G2P Registry: Individual ([g2p_registry_individual](g2p_registry_individual))**:  Integrates with the individual registrant model to handle change requests related to individual data.
    * **G2P Registry: Group ([g2p_registry_group](g2p_registry_group))**:  Extends group registrant functionality to manage changes related to group information.
    * **G2P Registry: Membership ([g2p_registry_membership](g2p_registry_membership))**:  Allows for change requests involving membership details, such as adding or removing members from groups.

2. **OpenSPP Service Points ([spp_service_points](spp_service_points))**: Integrates with the Service Points module to enable the submission of change requests through designated service points.

3. **OpenSPP Area ([spp_area](spp_area))**: Utilizes the Area module to manage change requests related to a registrant's geographical location, such as changes in address or district. 

4. **OpenSPP Scan ID Document ([spp_scan_id_document](spp_scan_id_document))**: Integrates with the ID scanning functionality to allow for the capture and association of scanned documents as supporting evidence for change requests.

5. **OpenSPP DMS ([spp_dms](spp_dms))**: Leverages the Document Management System for storing and managing documents related to change requests, such as proof of identity, address verification, or other supporting materials. 

6. **Phone Validation (`phone_validation`)**: Utilizes the phone validation module to ensure phone number updates within change requests adhere to proper formatting and validation rules.

## Additional Functionality

## Change Request Management

* **Change Request Model (`spp.change.request`)**: A central model for tracking all change requests, storing details like request type, status, applicant, assigned personnel, approval history, and related documents. 
* **Configurable Workflow**: Supports customizable multi-stage approval processes, allowing administrators to define the required steps and user roles involved in validating change requests.
* **Status Tracking**: Monitors the progress of change requests through various states (Draft, Pending Validation, Validated, Applied, Rejected, Cancelled), providing real-time visibility into the process. 
* **Audit Trail**:  Maintains a comprehensive history of all actions related to a change request, including submission, validation, approvals, rejections, and application, ensuring accountability and transparency.

## Integration with Registrant Data

* **Dynamic Form Generation**:  The module allows for defining different change request types, each associated with a specific form that captures the necessary data for that type of modification.
* **Data Validation**: Implements validation rules to ensure the data entered in change request forms meet specific criteria, such as data type, format, or range, before submission for approval. 
* **Automatic Data Update**:  Upon approval and application of a change request, the module automatically updates the corresponding registrant data in the relevant G2P Registry module, ensuring data consistency.

## User Interface and Experience

* **Dedicated Change Request Menu**:  Provides a centralized location within the OpenSPP interface for accessing and managing change requests.
* **User-Friendly Forms**:  Offers intuitive and easy-to-use forms for submitting different types of change requests, guiding users through the required information.
* **Role-Based Access Control**: Restricts access to change request functionalities based on user roles and permissions, ensuring data security and appropriate authorization levels.

## Conclusion

The OpenSPP Change Request module significantly strengthens the data management capabilities of OpenSPP by introducing a structured and controlled mechanism for handling modifications to registrant information.  By integrating with various core modules, the [spp_change_request](spp_change_request) module promotes data integrity, transparency, and accountability throughout the change management process. 
