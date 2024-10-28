# OpenSPP Audit Post

This document outlines the **G2P Registry: Audit Post** module within the OpenSPP platform. This module extends the functionality of the audit log by enabling the posting of audit log messages to related parent records.

## Purpose

The module's primary goal is to provide a comprehensive overview of changes not just within a single record, but also across related records in a parent-child relationship. By posting audit log information to parent records, it offers a centralized view of how modifications cascade through interconnected data.

## Module Integration and Dependencies

* **[spp_audit_log](spp_audit_log)**: This module directly depends on the audit log module. It leverages the existing audit log framework to capture and display change information. 
* **Mail (mail)**: The module utilizes the standard Odoo Mail module to post audit log messages as messages on parent records. This integration ensures that relevant stakeholders are notified about changes impacting related data.

## Additional Functionality

1. **Parent-Child Rule Association**:
    * Allows users to define parent-child relationships between audit rules. 
    * When an audit rule has a parent rule, changes logged by the child rule are also posted to the parent record.

2. **Field-Level Linking**:
    * Enables users to specify the relational field that connects the child model to the parent model within the audit rule configuration.
    * Ensures that the audit log messages are posted to the correct parent records based on the defined relationship.

3. **Enhanced Audit Log Model ([spp.audit.log](spp.audit.log))**:
    * Introduces new fields to store information about the parent record:
        * **parent_model_id:** Stores the model ID of the parent record.
        * **parent_res_ids_str:** Stores a comma-separated string of IDs representing the parent records.
        * **parent_data_html:**  Provides a formatted HTML representation of the changes made to the child record, intended for display on the parent record's message thread.

4. **Automated Message Posting**:
    * When a change is audited and a parent rule is defined, the module automatically generates a message on the parent record's message thread.
    * The message includes detailed information about the change, including the model, field, old value, and new value, presented in a user-friendly HTML format.

## Conclusion

The **G2P Registry: Audit Post** module enhances data transparency and traceability within OpenSPP by extending audit logging to encompass related records. This functionality provides valuable insights into how modifications propagate through the system, facilitating better data management and analysis. This is particularly beneficial in complex data structures where understanding the impact of changes across related records is crucial. 
