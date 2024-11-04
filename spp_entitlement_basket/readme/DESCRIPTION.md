# OpenSPP Entitlement Basket

This document outlines the functionality of the **OpenSPP Entitlement Basket** module. This module extends OpenSPP's program management by introducing the concept of predefined "baskets" of goods and services that beneficiaries are entitled to receive.

## Purpose

The **OpenSPP Entitlement Basket** module aims to:

* **Define In-Kind Entitlement Baskets:** Create predefined sets of products (goods and services) representing a complete entitlement package.
* **Simplify In-Kind Entitlement Management:** Streamline the assignment of multiple products to beneficiaries using a single basket.
* **Integrate with Program Cycles and Inventory:** Seamlessly connect entitlement baskets to program cycles and leverage existing inventory management features.

## Module Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)**: Uses the base registry for core beneficiary information and links basket entitlements to beneficiary profiles.

2. **[g2p_programs](g2p_programs)**:  Extends program management by introducing a new entitlement manager type for basket distribution.

3. **[spp_programs](spp_programs)**: Leverages the in-kind entitlement model and inventory integration features. 

4. **[spp_service_points](spp_service_points)**: Associates entitlement baskets with service points for beneficiary redemption.

5. **[product](product)**:  Utilizes the product module to define the goods and services included within an entitlement basket.

6. **[stock](stock)**:  Integrates with the stock module to manage inventory levels of basket products, generate procurement requests, and track stock movements upon entitlement approval. 

## Additional Functionality

* **Entitlement Basket Model (spp.entitlement.basket):** Introduces a new model to define entitlement baskets, capturing:
    * **Products:** A list of products included in the basket.
    * **Quantity per Product:** The number of units of each product a beneficiary is entitled to.

* **Basket Entitlement Manager (g2p.program.entitlement.manager.basket):**  
    * A new entitlement manager type specifically for managing basket distribution within a program.
    * Associates a program cycle with a predefined entitlement basket.
    * Allows configuration of optional multipliers based on beneficiary attributes (e.g., number of family members).
    * Handles the generation of individual in-kind entitlements for each product in the basket based on beneficiary eligibility and multiplier settings.

* **Inventory Integration:**
    * When a basket entitlement is approved, the module leverages existing [spp_programs](spp_programs) functionality to:
        * Generate procurement requests for the required quantities of basket products within the designated warehouse. 
        * Trigger stock movements to transfer goods from the warehouse to the designated service point for beneficiary redemption.

* **Beneficiary Entitlement View:** Extends the beneficiary profile to display a history of received entitlement baskets and the individual product entitlements within each basket.

## Conclusion

The **OpenSPP Entitlement Basket** module simplifies the management and distribution of complex in-kind entitlements. By bundling products into predefined baskets, it streamlines program configuration, improves efficiency, and enhances transparency for both program administrators and beneficiaries. The integration with existing OpenSPP modules ensures a cohesive and robust system for managing diverse social protection programs. 
