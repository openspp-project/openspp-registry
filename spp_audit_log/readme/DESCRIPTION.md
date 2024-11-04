# OpenSPP Audit Log

This module provides audit logging functionality for OpenSPP, enabling the tracking of changes made to specific data within the system. It helps maintain data integrity, accountability, and provides a historical record of modifications.

## Purpose

The **SPP Audit Log** module is designed to:

* **Record Data Changes:** Automatically log changes made to specified fields within selected models.
* **Track User Actions:**  Identify the user responsible for each data modification.
* **Provide an Audit Trail:**  Maintain a chronological log of changes, including old and new values, for review and analysis.

## Module Dependencies and Integration

1. **Base (base)**:  The module relies on Odoo's core features for models, views, security groups, and user management.

2. **Mail (mail):** Leverages the messaging functionality for potential future enhancements related to audit log notifications. 

3. **G2P Registry: Membership ([g2p_registry_membership](g2p_registry_membership)):** This dependency appears to be related to a specific use case and might not be a core dependency for the audit log functionality.  It could indicate that the audit log is being used to track changes within the group membership model.

## Additional Functionality

The module introduces the following key elements:

* **Audit Rule Model ([spp.audit.rule](spp.audit.rule)):**
    * Allows administrators to define rules specifying which models and fields should have their changes logged.
    * Provides options to log the creation, update, or deletion of records.
    * Includes a feature to automatically add a "View Logs" button to the related model's form view for easy access to audit logs. 

* **Audit Log Model ([spp.audit.log](spp.audit.log)):**
    * Stores the audit log entries, capturing details like timestamp, user, model, record ID, type of operation (create/write/unlink), and the changes made (old and new values).
    * Provides a computed field to display the changed data in a user-friendly HTML format within the audit log form view. 

* **Audit Decorator:** 
    * Utilizes a decorator function to automatically intercept and log changes made to models and fields defined by the audit rules. This simplifies the implementation and ensures that auditing is applied consistently. 

* **Security Groups:**
    * Introduces a new security group, "Manager," to manage access to audit log rules and logs, restricting sensitive information from unauthorized users.

* **User Interface:**
    * Adds menu items for managing audit rules and viewing audit logs, providing centralized access points within the OpenSPP interface. 

## Conclusion

The **SPP Audit Log** module enhances the accountability and transparency of the OpenSPP platform. By meticulously tracking data changes and user actions, it provides administrators with a valuable tool for auditing, troubleshooting, and maintaining data integrity. The module's flexible rule system and tight integration with core Odoo features make it adaptable to a variety of data tracking requirements within the OpenSPP ecosystem. 
