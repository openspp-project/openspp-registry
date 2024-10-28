# OpenSPP Custom Filter UI

This document outlines the functionality of the **G2P Registry: Custom Fields UI** module within the OpenSPP ecosystem. This module, depending on the **[g2p_registry_base](g2p_registry_base)** module, provides a user-friendly interface for defining and managing custom fields for registrants. These custom fields allow implementers to tailor the registry to their specific program needs by capturing additional data beyond the core fields provided by the base module.

## Purpose

The **G2P Registry: Custom Fields UI** module aims to:

* Simplify the process of adding and modifying custom fields for registrants.
* Provide a centralized location within the Odoo backend to manage these fields.
* Offer flexibility in defining field types, validation rules, and display options.

## Module Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)**: This module depends on the **G2P Registry: Base** module, which provides the fundamental structure for storing and managing registrant data. The custom fields created through this UI module are directly integrated as extensions to the registrant profiles managed by the base module.

2. **Base (base)**:  Leverages the Odoo Base module for core functionalities like user interface elements, data models, and access control. 

## Additional Functionality

The key features provided by the **G2P Registry: Custom Fields UI** module include:

* **Custom Field Creation Wizard:** Offers a streamlined process to define new custom fields, guiding users through selecting the appropriate field type, label, and other relevant properties.
* **Field Type Selection:** Supports various field types available within Odoo, such as Char, Integer, Selection, Date, Many2one (relational fields), and more, enabling storage of different data formats.
* **Target Specificity:**  Allows users to specify whether a custom field applies to individual registrants or groups, ensuring data is collected at the appropriate level.
* **Field Category Distinction:**  Differentiates between custom fields that capture directly entered data and those that are calculated based on other field values, allowing for automatic data derivation. 
* **Integration with Group Membership Kinds:** For calculated fields, provides the option to associate the calculation with specific group membership types defined within the system.
* **Presence Indicator:** For calculated fields, includes the ability to configure a boolean "presence" indicator, simplifying the tracking of specific criteria related to group memberships.

## Conclusion

The **G2P Registry: Custom Fields UI** module empowers users to adapt the OpenSPP registry to their unique requirements without the need for extensive technical customization. Its intuitive interface and tight integration with the **[g2p_registry_base](g2p_registry_base)** module simplify the management of custom data, enhancing the flexibility and utility of the OpenSPP platform for diverse social protection programs. 
