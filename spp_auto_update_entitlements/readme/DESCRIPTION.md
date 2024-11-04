# OpenSPP Auto-Update Entitlements

This document describes the **OpenSPP Auto-Update Entitlements** module within the OpenSPP platform. This module enhances the management of entitlement lifecycles by automatically updating entitlement states when program cycles end. This automation streamlines benefit administration and provides a more accurate view of benefit utilization.

## Purpose

The **OpenSPP Auto-Update Entitlements** module primarily focuses on:

* **Automating Entitlement State Transitions**: Automatically updates the status of entitlements at the end of a program cycle based on their redemption status.
* **Improving Data Accuracy**: Provides a more accurate reflection of entitlement utilization by automatically transitioning entitlements to appropriate states (e.g., "Partially Redeemed/Paid to Beneficiary", "Redeemed/Paid to Beneficiary"). 
* **Reducing Manual Effort**: Eliminates the need for manual updates of entitlement states, freeing up program administrators to focus on other tasks.

## Module Dependencies and Integration

1. **[OpenSPP Entitlement Transactions](spp_ent_trans)**: 
    * Heavily relies on this module to access transaction histories associated with entitlements.
    * Uses transaction data to determine the redemption status of entitlements and trigger appropriate state updates.

2. **[g2p_programs](g2p_programs)**: 
    * Integrates with the core program management module to access program cycle data. 
    * Leverages cycle end dates to initiate the automatic update process for entitlements associated with the ending cycle.

3. **[OpenSPP Programs](spp_programs)**: 
    * Builds upon the OpenSPP Programs module's functionality for managing both cash and in-kind entitlements.
    * Extends entitlement models and views to accommodate the automatic state update logic.

## Additional Functionality

* **Cycle End State Check**:  When a program cycle is marked as ended, the module automatically analyzes the transaction history of each associated entitlement.

* **Entitlement State Logic**:  Based on transaction data, the module applies the following logic to update entitlement states:
    * **Partially Redeemed/Paid to Beneficiary**: If an entitlement has transactions but still has a remaining balance, its state changes to "Partially Redeemed/Paid to Beneficiary".
    * **Redeemed/Paid to Beneficiary**: If an entitlement has been fully redeemed with no remaining balance, its state transitions to "Redeemed/Paid to Beneficiary".
    * **Unredeemed**: If an entitlement has no associated transactions, its state remains unchanged. 

* **UI Enhancements**:
    * Modifies the cycle view to automatically mark a cycle as expired when its end date is in the past.
    * Extends entitlement views to display the calculated `entitlement_balance` based on the associated transaction history.

## Conclusion

The **OpenSPP Auto-Update Entitlements** module improves the accuracy and efficiency of entitlement management in OpenSPP. By automating state transitions based on actual benefit utilization, it provides program administrators with a more reliable view of program operations while reducing manual administrative tasks. 
