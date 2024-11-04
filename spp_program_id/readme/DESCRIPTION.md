# OpenSPP Program ID

This document describes the **OpenSPP Program ID** module, an extension to the OpenSPP platform. This module enhances the existing **OpenG2P: Programs** functionality by adding unique, system-generated IDs to each program for improved tracking and reference.

## Purpose

The **OpenSPP Program ID** module aims to:

* **Provide Unique Program Identification**:  Generate and assign a distinct ID to each program, allowing for easy identification and reference.
* **Enhance Data Management**:  Improve the organization and management of program data by introducing a standardized identification system.
* **Facilitate Integration**: Enable seamless integration with other systems or modules by providing a consistent program identifier.

## Module Dependencies and Integration

1. **[spp_programs](spp_programs)**: 
    * Leverages the core program management features provided by the OpenSPP Programs module.
    * Extends program models and views to incorporate the program ID field.

2. **[g2p_programs](g2p_programs)**: 
    * Builds upon the program structure and functionality provided by the G2P Programs module.
    * Integrates with program views to display the generated program ID.

## Additional Functionality

* **Program ID Generation**: 
    * Automatically generates a unique program ID using a defined sequence (`program.id.sequence`) upon program creation.
    * Ensures that each program has a distinct identifier.

* **Program ID Field**: 
    * Introduces a new field, `program_id`, in the `g2p.program` model to store the generated unique ID.
    * Makes the `program_id` field read-only to prevent accidental modification.

* **View Integration**:
    * Integrates the `program_id` field into relevant program views:
        * **Search Filter**: Adds `program_id` as a search filter option in the program list view.
        * **List View**: Displays the `program_id` alongside other program details in the program list view. 
        * **Form View**: Shows the `program_id` prominently within the program form view.

## Conclusion

The **OpenSPP Program ID** module enhances the OpenSPP platform by providing a simple yet powerful mechanism for uniquely identifying programs. This enhancement contributes to better data management, easier referencing, and smoother integration with other systems, ultimately improving the efficiency and usability of the OpenSPP platform. 
