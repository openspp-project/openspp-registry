# OpenSPP Manual Entitlement

This document describes the **OpenSPP Manual Entitlement** module, which extends the OpenSPP system to allow for manual entitlement creation within social protection programs. 

## Purpose

The **OpenSPP Manual Entitlement** module aims to:

* **Enable Manual Entitlement Creation:** Provide a mechanism for program administrators to manually generate entitlements for beneficiaries in cases where automated processes are not suitable. This is particularly useful for programs with specific eligibility criteria or where beneficiary data might not be readily available for automated processing.

* **Integrate with Existing Program Cycles:**  Seamlessly integrate with the existing program cycle structure in OpenSPP, allowing for manual entitlement creation within defined cycle periods.

* **Enhance Flexibility in Entitlement Management:**  Offer a more flexible approach to entitlement management, accommodating situations where automated rules might not cover all beneficiary scenarios. 

## Dependencies and Integration

1. **Queue Job** ([queue_job](queue_job)): Utilizes the Queue Job module for asynchronous processing of entitlement creation, preventing performance issues when handling large numbers of beneficiaries.

2. **G2P Registry: Base** ([g2p_registry_base](g2p_registry_base)):  Depends on the G2P Registry: Base module to access and manage registrant data, ensuring that entitlements are linked to the correct beneficiary profiles.

3. **OpenSPP Registrant Import** ([spp_registrant_import](spp_registrant_import)): Integrates with the OpenSPP Registrant Import module to potentially streamline the process of importing beneficiary lists for manual entitlement creation. 

4. **G2P Programs** ([g2p_programs](g2p_programs)):  Extends the G2P Programs module by adding functionality to create manual entitlements within the existing program and cycle structures.

## Additional Functionality

* **Manual Entitlement Wizard:** 
    * Introduces a wizard that guides users through the manual entitlement creation process.
    * Allows selection of a specific program cycle for which to create entitlements.
    * Provides an interface to either select existing beneficiaries or import a list of beneficiaries for entitlement generation.
    * Includes a step to review and confirm entitlement details before creation.

* **Manual Entitlement Manager:**
    * Extends the `g2p.program.entitlement.manager.default` model to include a flag `is_manual_cash`.
    * Adds a method `manual_prepare_entitlements` to handle the creation of entitlements based on data provided through the wizard.

* **Cycle View Extension:**
    * Modifies the program cycle view to include a button to trigger the manual entitlement wizard.
    * Provides a visual cue within the cycle view to indicate if manual entitlement is enabled for the program. 

## Conclusion

The **OpenSPP Manual Entitlement** module enhances the flexibility of OpenSPP's entitlement management system. By enabling manual entitlement creation, it empowers program administrators to handle situations where automated rules might not be sufficient, ensuring that all eligible beneficiaries receive their entitled benefits.  This module contributes to a more inclusive and adaptable social protection program implementation. 
