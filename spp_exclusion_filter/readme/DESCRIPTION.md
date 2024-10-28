# OpenSPP Exclusion Filter

This document outlines the functionality of the **OpenSPP Exclusion Filter** module.  This module enhances the program creation process within OpenSPP by introducing exclusion filters during the program wizard. 

## Purpose

The **OpenSPP Exclusion Filter** module aims to:

* **Streamline Program Targeting**:  Simplify the process of excluding specific registrant groups during program creation, ensuring that benefits are directed to the intended population.
* **Improve Efficiency**:  Reduce manual effort required to identify and exclude ineligible registrants from new programs.
* **Enhance Program Accuracy**:  Minimize the risk of including ineligible beneficiaries by applying pre-defined exclusion criteria. 

## Module Dependencies and Integration

1. **[spp_programs](spp_programs)**: 
    * Integrates with the OpenSPP program creation wizard, adding a dedicated step for configuring exclusion filters.
    * Leverages program data, such as target criteria and program objectives, to guide the selection of relevant exclusion filters. 

2. **[g2p_registry_base](g2p_registry_base)**:
    * Utilizes registrant data, including demographics, tags, and relationships, to apply exclusion filters.
    * Accesses the registry to identify and flag registrants who meet the specified exclusion criteria. 

3. **[g2p_programs](g2p_programs)**:
    * Extends the functionality of OpenG2P's program creation process.
    * Ensures compatibility with existing program management features and workflows.

## Additional Functionality

* **Program Wizard Integration**:
    * Adds a dedicated step to the program creation wizard, allowing program managers to select and configure exclusion filters. 
    * Provides a user-friendly interface for defining exclusion criteria and previewing the potential impact on the target population.

* **Eligibility Manager Integration (Potentially)**: 
    * May integrate with existing eligibility managers to leverage pre-defined eligibility rules as exclusion criteria.
    * Could offer the flexibility to create exclusion filters based on combinations of eligibility criteria.

* **Automated Exclusion**:
    * Upon program creation, the module automatically applies the selected exclusion filters to the registry.
    * Flags registrants who meet the exclusion criteria, preventing them from being considered for enrollment in the program.

## Conclusion

The **OpenSPP Exclusion Filter** module streamlines program targeting by introducing a structured approach to excluding ineligible registrants during program creation. Its integration with the OpenSPP program wizard, reliance on registry data, and potential integration with eligibility managers enhance the efficiency and accuracy of program implementation. 
