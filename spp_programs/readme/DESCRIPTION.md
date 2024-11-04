# OpenSPP Programs

This document outlines the functionality of the **OpenSPP Programs** module.  This module extends the **OpenG2P: Programs** functionality, introducing in-kind entitlement management alongside existing cash-based features.

## Purpose

The **OpenSPP Programs** module aims to:

* **Manage In-Kind Entitlements**:  Introduce the concept of in-kind entitlements alongside cash entitlements, allowing programs to distribute goods and services.
* **Integrate with Inventory**: Link in-kind entitlements to the Odoo Inventory module, enabling stock management, procurement, and tracking of distributed items.
* **Enhance Existing Program Features**: Extend OpenG2P's program management with capabilities tailored for in-kind distributions.

## Module Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)** : Leverages the base registry for core registrant information and extends it by adding in-kind entitlement tracking to registrant profiles.

2. **[g2p_programs](g2p_programs)**: 
    * Builds upon the core program management features, including program creation, cycle management, and eligibility determination.
    * Extends program views to incorporate in-kind entitlement data and actions.

3. **[spp_area](spp_area)**: Integrates with the area module to associate service points for in-kind entitlement redemption with specific geographical areas.

4. **Product (product)**: Utilizes the product module to define the goods and services offered as part of in-kind entitlements, leveraging existing product information and categorization.

5. **Stock (stock)**: 
    * Links in-kind entitlements to the stock module, enabling the generation of stock movements upon entitlement approval.
    * Allows for the tracking of inventory levels, procurement needs, and the flow of goods from warehouses to beneficiaries.

## Additional Functionality

* **In-Kind Entitlement Model (g2p.entitlement.inkind)**: Introduces a new model specifically for managing in-kind entitlements, capturing data such as:
    * **Product**: The specific good or service being distributed.
    * **Quantity**: The number of units entitled to the beneficiary.
    * **Unit Price**: The value of each unit for accounting and reporting.
    * **Warehouse**:  The location from which the item will be distributed.
    * **Service Point**: The designated point where beneficiaries can redeem their entitlements.

* **Inventory Integration**:
    * When an in-kind entitlement is approved:
        * A procurement request is automatically generated within the stock module.
        * Stock movements are triggered to transfer the goods from the warehouse to the designated service point.

* **Extended Program Views**:
    * Program views are modified to display both cash and in-kind entitlement counts.
    * New tabs and fields within program forms provide visibility into in-kind entitlement details. 

* **Registrant Profile Enhancements**:
    * Registrant profiles now include a dedicated section for tracking in-kind entitlements, listing past and current entitlements.
    * Provides a consolidated view of a registrant's benefits, encompassing both cash and in-kind distributions. 

* **Reporting**:
    * The module includes new reports specifically designed for in-kind entitlements, providing insights into:
        * Distribution of goods and services.
        * Inventory levels and procurement needs.
        * Service point activity and redemption rates.

## Conclusion

The **OpenSPP Programs** module significantly expands the OpenG2P platform's capabilities by incorporating in-kind entitlement management.  This integration with inventory management and the enhancements to existing program features make OpenSPP a comprehensive solution for managing a wider range of social protection and agricultural support programs. 
