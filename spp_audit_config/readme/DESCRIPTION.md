# OpenSPP Audit Config

This document outlines the **OpenSPP Audit Config** module within the OpenSPP platform. This module is responsible for configuring and managing audit rules used to track and log changes made to critical data within the system.

## Purpose

The primary purpose of the **OpenSPP Audit Config** module is to:

* **Define Audit Rules:** Establish specific rules that determine which data models, fields, and actions (create, update, delete) should be monitored and logged.
* **Enhance Data Security:** Provide an auditable trail of changes made to sensitive information, ensuring accountability and enabling investigations into unauthorized modifications.
* **Improve Data Integrity:**  By logging changes, the module helps identify potential data inconsistencies or errors introduced during data entry or updates.

## Module Integration and Dependencies

The **OpenSPP Audit Config** module works in conjunction with other modules to provide comprehensive audit logging:

* **[SPP Audit Log](spp_audit_log)**: This module is responsible for storing the actual audit logs generated based on the configured rules. The Audit Config module defines **what** to log, and the Audit Log module handles **how** it is logged and stored.
* **[SPP Audit Post](spp_audit_post)**: The Audit Post module provides the mechanisms for reviewing and managing the generated audit logs. It offers interfaces to view, filter, and analyze the log data.

**Integration with Other Modules:**

The **OpenSPP Audit Config** module's functionality is designed to be applied across various OpenSPP modules.  It can define audit rules for any module that requires change tracking, such as:

* **[SPP Service Points](spp_service_points)**: Track changes to service point information, including location, contact details, and operational status.
* **[G2P Registry: Membership](g2p_registry_membership)**: Monitor modifications to individual memberships within groups, ensuring accurate representation of group composition.
* **[OpenSPP Programs](spp_programs)**: Log any updates to program configurations, eligibility criteria, or benefit distribution details.

## Additional Functionality

1. **Audit Rule Definition:** 
   *  Provides a user-friendly interface to define audit rules. 
   * **Key configuration options include:**
      * **Model:** Specify the data model to be audited (e.g., `spp.service.point`, `g2p.group.membership`).
      * **Fields:** Select the specific fields within the model that require logging (e.g., `name`, `status`, `start_date`).
      * **Actions:**  Choose which actions should trigger a log entry:
         * **Create:** Log the creation of new records.
         * **Write:** Log any modifications made to existing records.
         * **Unlink:** Log the deletion of records.
   * **Advanced Rule Configuration:** The module supports defining hierarchical audit rules:
      * **Parent-Child Relationships:**  Link audit rules to create a parent-child hierarchy. This allows for more granular logging, capturing changes to related records. For example, if a service point is linked to a program, any changes to the service point can trigger logs for both the service point itself and the associated program.
      * **Connecting Fields:** When defining hierarchical rules, the module lets you specify the field that connects the parent and child records.

2. **Predefined Audit Rules:**
   * The module includes a set of predefined audit rules for common data models and fields within the OpenSPP system. These rules provide a starting point for implementing audit logging and can be customized further based on specific needs.

3. **Data/audit_rule_data.xml:** 
    * This file contains predefined audit rules that are loaded during the module installation. This ensures essential auditing is in place from the start.

## Conclusion

The **OpenSPP Audit Config** module plays a crucial role in enhancing data security and integrity within the OpenSPP platform. By enabling the configuration of flexible and comprehensive audit rules, the module provides administrators with the tools to track changes, ensure accountability, and maintain the reliability of critical data across various OpenSPP modules. 
