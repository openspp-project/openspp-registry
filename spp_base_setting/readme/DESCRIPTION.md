# OpenSPP Base Settings

This document outlines the functionality and purpose of the **OpenSPP Base Settings** module within the OpenSPP ecosystem. This module builds upon the foundational [g2p_registry_base](g2p_registry_base) module to provide essential configuration options for OpenSPP deployments.

## Purpose

The **OpenSPP Base Settings** module aims to:

* **Customize the Odoo interface for OpenSPP:**  Adapts existing Odoo views and menus to align with OpenSPP terminology and workflows.
* **Centralize OpenSPP-specific configurations:**  Provides a dedicated location for managing settings relevant to OpenSPP implementations.

## Module Dependencies and Integration

1. [g2p_registry_base](g2p_registry_base): This module inherits the core registry functionalities provided by the **G2P Registry: Base** module, including managing registrants, relationships, and identification.

2. **Base (base):** Leverages the core Odoo [Base](Base) module for data models, views, and basic functionalities.

## Additional Functionality

The **OpenSPP Base Settings** module introduces:

* **Country Office Management:**  Repurposes the Odoo Company model (`res.company`) to represent Country Offices, providing a centralized view of information related to each office.
* **User Interface Adaptations:**
    * Modifies the `res.company` form view to better reflect the concept of a Country Office.
    * Adds a dedicated menu item for managing Country Offices. 
    * Integrates User and Group management within the OpenSPP configuration menu structure. 

## Key Concepts 

* **Country Offices:** The module redefines the standard Odoo "Company" as a "Country Office," reflecting the organizational structure common in OpenSPP deployments. This allows administrators to manage settings and data specific to each country office.

## Conclusion

The **OpenSPP Base Settings** module provides the necessary configurations and customizations to tailor the Odoo environment for OpenSPP implementations. By building upon existing modules and adapting core functionalities, it streamlines the setup and management of OpenSPP deployments. 
