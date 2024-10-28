# OpenSPP Custom Field

This document describes the **OpenSPP Custom Field** module, which extends the functionality of OpenSPP by adding customizable fields to registrant profiles. This module is specifically designed to work with the **[g2p_registry_base](g2p_registry_base)** module and leverages its features for managing registrant data.

## Purpose

The **OpenSPP Custom Field** module enables administrators to define and manage custom fields for capturing additional information about registrants. This allows for greater flexibility and adaptability in tailoring the registry system to specific program needs and data collection requirements.

## Integration with [g2p_registry_base](g2p_registry_base)

This module directly integrates with the **[g2p_registry_base](g2p_registry_base)** module by extending the functionality of the `res.partner` model, which is the core model for managing registrants within OpenSPP.  Instead of creating new models or data structures, it adds custom fields directly onto the registrant profile, ensuring data consistency and ease of management.

## Key Functionality

* **Custom Field Creation**:  Administrators can create various types of custom fields (e.g., text fields, booleans, dates) through Odoo's standard field creation mechanisms.
* **Field Categorization**: Custom fields are categorized as either "Custom Details" or "Indicators." This allows for logical grouping and display of information within the registrant profile.
* **Conditional Field Display**:  Fields can be configured to display based on whether the registrant is an individual or a group, ensuring relevant information is presented in each context.
* **Indicators as Read-Only**:  Fields categorized as "Indicators" are automatically set as read-only on the user interface. This is particularly useful for displaying calculated metrics or data points derived from other system information.
* **Seamless UI Integration**:  Custom fields are integrated directly into the registrant profile form within the Odoo interface. This provides a user-friendly experience for data entry and management without requiring navigation to separate sections or modules. 

## Benefits

* **Enhanced Data Collection**:  Capture program-specific information beyond the standard fields provided by the **[g2p_registry_base](g2p_registry_base)** module.
* **Improved Targeting and Analysis**: Utilize custom fields to segment registrants, analyze trends, and support data-driven decision-making.
* **Flexibility and Adaptability**:  Easily modify and extend the registry system to accommodate evolving program needs and data collection requirements. 

## Conclusion

The **OpenSPP Custom Field** module provides a powerful and flexible way to customize the OpenSPP registry system. By seamlessly integrating with the **[g2p_registry_base](g2p_registry_base)** module and leveraging Odoo's existing framework, it empowers administrators to tailor data collection and management processes to meet the specific requirements of their social protection programs. 
