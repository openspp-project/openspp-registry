# OpenSPP User Roles

## Overview

The [spp_user_roles](spp_user_roles.md) module enhances the user role management capabilities of OpenSPP, providing a more granular and context-aware approach to user permissions. It builds upon the base user role system in Odoo and introduces the concept of "local" roles, allowing administrators to assign permissions based on specific geographical areas.

## Purpose

This module aims to:

- **Define Local Roles:** Introduce the concept of roles that are specific to a particular geographical area (e.g., Center Area).
- **Restrict User Access:**  Limit the access of users with local roles to data and operations within their assigned areas.
- **Enhance Data Security:** Improve data security by ensuring that users can only view and modify information relevant to their assigned locations. 

## Dependencies and Integration

1. **G2P Registry: Base ([g2p_registry_base](g2p_registry_base.md)):**  This module indirectly depends on the `res.partner` model from the G2P Registry: Base module, as it modifies the access rules for registrant data based on a user's assigned areas.

2. **G2P Registry: Group ([g2p_registry_group](g2p_registry_group.md)):**  Similar to the Base module, it impacts access to group registrant data based on area assignments.

3. **G2P Programs ([g2p_programs](g2p_programs.md)):**  The module's area-based access control can be applied to program-related data, ensuring that users with local roles only see and manage programs operating within their designated areas.

4. **OpenSPP Area ([spp_area](spp_area.md)):**  The module heavily relies on the area hierarchy defined in the [spp_area](spp_area.md) module. Local roles are directly associated with specific areas, and user access is restricted accordingly.

5. **OpenSPP ID Queue ([spp_idqueue](spp_idqueue.md)):**  Integrates with the ID Queue module to control access to ID card requests and batches based on area assignments, ensuring that users only manage requests originating from their designated locations.

6. **Base User Role (base_user_role):**  Extends the base Odoo module for user role management, inheriting its core functionalities and adding the area-based restrictions.

7. **OpenSPP API ([spp_api](spp_api.md)):**  The module's access control mechanism is integrated with the OpenSPP API, ensuring that API requests from users with local roles are filtered to return only data within their authorized areas.

## Additional Functionality

* **Role Type (role_type):** 
    * Adds a new field to the `res.users.role` model to distinguish between "global" roles (with system-wide access) and "local" roles (restricted to specific areas).

* **Local Area (local_area_id):** 
    * Introduces a field in the `res.users.role.line` model to associate local roles with specific areas.
    * This field is only visible and editable for roles marked as "local."

* **Center Area IDs (center_area_ids):**
    * Adds a computed field to the `res.users` model to store the areas assigned to a user through their local roles.

* **Area-Based Data Filtering:**
    * Modifies the search methods for models like `res.partner` to automatically include area-based filters when accessed by users with local roles. 
    * Ensures that users only see data relevant to their assigned areas.

* **API Integration:**
    * Integrates with the OpenSPP API to enforce area-based access control for API requests.
    * API responses for users with local roles are automatically filtered to include only data within their authorized locations.

## Conclusion

The [spp_user_roles](spp_user_roles) module significantly enhances the security and granularity of user permissions in OpenSPP. By introducing local roles and area-based access control, it ensures that users can only access and manage information within their designated geographical areas. This is particularly crucial for large-scale programs with decentralized operations, where different teams or individuals are responsible for specific regions. 
