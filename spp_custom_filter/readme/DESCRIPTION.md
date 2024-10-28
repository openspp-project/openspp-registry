# OpenSPP Custom Filter

## Overview

The SPP Custom Filter module enhances the default Odoo filtering functionality by allowing administrators to control which fields are displayed in the filter dropdown menus. This is particularly useful for complex models with a large number of fields, where displaying all fields in the filter dropdown can be overwhelming and impact usability. 

## Features

- **Granular control over filterable fields:** Administrators can enable or disable the "Show on Custom Filter" option for individual fields in any model. This allows them to selectively expose only the most relevant fields for filtering in the user interface.

- **Improved User Experience:** By limiting the number of fields displayed in the filter dropdown menus, users are presented with a cleaner and more focused interface. This simplifies the process of finding and filtering data, ultimately improving efficiency.

## How it Works

1. **Field Configuration:** The module adds a new boolean field, "Show on Custom Filter," to the field definition in the Odoo backend. By default, this option is disabled for all fields.

2. **Enabling Custom Filtering:** Administrators can enable the "Show on Custom Filter" option for specific fields within a model. Only the fields with this option enabled will appear in the filter dropdown menus for that model.

3. **User Interface Integration:** The module seamlessly integrates with the existing Odoo filtering mechanism. Users will see the filtered fields in the dropdown menus as usual, but with only the selected fields available.

## Dependencies

This module depends on the following Odoo module:

- **base:** This module is a core Odoo module that provides the basic framework and functionalities. 

## Integration with Other Modules

The [SPP Custom Filter](SPP Custom Filter) module can be used with any other Odoo module. Its functionality is generic and can be applied to enhance the filtering experience for any model.

## Example Use Case

Consider a Beneficiary model with numerous fields, such as name, age, address, contact details, program enrollment status, payment history, etc. Displaying all these fields in the filter dropdown menu can be overwhelming. With the [SPP Custom Filter](SPP Custom Filter) module, administrators can choose to display only frequently used fields for filtering, such as name, program enrollment status, and payment status, simplifying the user interface.

## Conclusion

The [SPP Custom Filter](SPP Custom Filter) module provides a simple yet powerful solution to enhance the usability of Odoo's filtering system. By offering administrators granular control over filterable fields, the module improves user experience and streamlines data management within Odoo.
