# OpenSPP Program Entitlement Basic Cash Spent 

This document details the **SPP Program Entitlement Basic Cash Spent** module within the OpenSPP platform. This module extends the functionality of the [g2p_programs](g2p_programs) module to specifically handle the tracking of cash spent for basic cash entitlement programs.

## Purpose

The **SPP Program Entitlement Basic Cash Spent** module provides a straightforward mechanism for:

* **Tracking Cash Spending**: Allows program administrators to record the amount of cash spent by beneficiaries against their allocated entitlements.
* **Calculating Remaining Balances**: Automatically calculates the remaining balance for each entitlement based on the initial amount and the recorded spending.
* **Monitoring Entitlement Utilization**: Facilitates the monitoring of how beneficiaries are utilizing their allocated cash benefits.

## Module Dependencies and Integration

1. **G2P Registry: Base ([g2p_registry_base](g2p_registry_base))**: Inherits core registry functionality for managing beneficiary information.
2. **[g2p_programs](g2p_programs)**:
    * Extends the **Entitlement (g2p.entitlement)** model to include cash spending tracking.
    * Leverages program and cycle structures for organizing and managing entitlements. 

## Additional Functionality

* **Spent Amount Tracking**: Introduces a new field, `spent_amount`, within the **Entitlement (g2p.entitlement)** model to record the amount of cash spent by the beneficiary.
* **Automatic Balance Calculation**: Automatically computes the remaining balance (`balance`) for each entitlement by subtracting the `spent_amount` from the `initial_amount`.
* **Currency Support**: Utilizes the existing `currency_id` field from the **Entitlement** model to ensure accurate tracking of spending in the appropriate currency. 

## Integration with Other Modules

This module seamlessly integrates with the [g2p_programs](g2p_programs) module by directly extending the **Entitlement** model. This integration allows for:

* **Centralized Entitlement Management**:  Cash spending information is directly associated with the corresponding entitlement record within the program cycle. 
* **Streamlined Reporting**: Enables the generation of reports that combine entitlement data (initial amount, validity period) with spending information (spent amount, balance).
* **Enhanced Monitoring and Evaluation**: Provides program administrators with a comprehensive view of entitlement utilization, supporting better decision-making and program adjustments. 

## Conclusion

The **SPP Program Entitlement Basic Cash Spent** module offers a simple yet effective solution for tracking cash spending within basic cash entitlement programs. By extending the core functionality of the [g2p_programs](g2p_programs) module, it ensures seamless integration and enhances the overall management and monitoring of program benefits. 
