# OpenSPP Custom Field Custom Filter

## Overview

The **SPP Custom Field - Custom Filter Integration** module bridges the functionality of the [G2P Registry: Custom Fields UI](G2P Registry: Custom Fields UI) module and the [SPP Custom Filter](SPP Custom Filter) module. It allows administrators to decide whether a custom field, created through the [G2P Registry: Custom Fields UI](G2P Registry: Custom Fields UI](G2P Registry: Custom Fields UI](G2P Registry: Custom Fields UI) module and the [SPP Custom Filter](SPP Custom Filter) module. It allows administrators to decide whether a custom field, created through the [G2P Registry: Custom Fields UI) module, should be available for filtering within the system. This integration provides a comprehensive approach to managing both the definition and usability of custom fields within the OpenSPP platform.

## Purpose

The primary goal of this module is to enhance the filtering capabilities of custom fields within OpenSPP. By enabling the "Allow Filter" option for specific custom fields, administrators can empower users to filter and analyze registry data based on these custom attributes. This granular control over filterable fields contributes to a more efficient and tailored user experience.

## Integration and Functionality

1. **Dependency on Custom Field Definition:** This module relies on the [G2P Registry: Custom Fields UI](G2P Registry: Custom Fields UI) module for the creation and management of custom fields. It extends the functionality of this module by adding a filtering dimension to the custom field definition.

2. **Integration with Custom Filter Logic:** It seamlessly integrates with the [SPP Custom Filter](SPP Custom Filter) module, which provides the underlying mechanism for controlling the visibility of fields in filter dropdowns. The "Allow Filter" option, added by this module, acts as a flag that the [SPP Custom Filter](SPP Custom Filter](SPP Custom Filter](SPP Custom Filter) module, which provides the underlying mechanism for controlling the visibility of fields in filter dropdowns. The "Allow Filter" option, added by this module, acts as a flag that the [SPP Custom Filter) module uses to determine whether to display a custom field in the filter interface.

3. **User Interface Enhancement:** From the user perspective, enabling the "Allow Filter" option for a custom field results in that field appearing as a selectable option in the filter dropdown menus, alongside standard fields. This allows users to construct specific queries and filter data based on the values stored in these custom fields.

## Example Use Case

Let's say a program using OpenSPP has defined a custom field called "Disability Status" to track the disability status of registrants.  By enabling the "Allow Filter" option for this custom field, program staff can easily filter the registry to identify and target interventions for registrants with specific disabilities.  This streamlines program operations and allows for more effective service delivery.

## Conclusion

The **SPP Custom Field - Custom Filter Integration** module plays a crucial role in maximizing the utility of custom fields within OpenSPP. By linking custom field definitions with filtering capabilities, this module provides a powerful tool for data analysis, reporting, and program implementation. It contributes to a more flexible and user-friendly system that can be readily adapted to the specific needs of diverse social protection programs. 
