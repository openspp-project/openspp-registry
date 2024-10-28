# OpenSPP Proxy Means Testing

This document describes the **OpenSPP Proxy Means Testing (spp_pmt)** module, which extends the OpenSPP framework to incorporate Proxy Means Testing (PMT) functionalities. This module allows program implementers to calculate a PMT score for groups of registrants based on specific criteria, aiding in the identification and prioritization of beneficiaries for social protection programs. 

## Purpose

The **spp_pmt** module aims to:

* **Enable Proxy Means Testing**:  Provide the tools to calculate a PMT score for groups of registrants, using weighted criteria relevant to the specific program context.
* **Customize PMT Criteria**:  Allow administrators to define and configure the criteria used in the PMT calculation, tailoring the assessment to their program's needs.
* **Integrate with Existing Registry Data**:  Leverage existing data from the OpenSPP registry modules to perform the PMT calculation, minimizing data duplication and ensuring consistency. 

## Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)** :  The **spp_pmt** module depends on the **G2P Registry: Base** module for access to core registrant data, including group memberships.  It utilizes this data to determine the individuals associated with each group and to retrieve their relevant attributes for the PMT calculation.

2. **[g2p_registry_group](g2p_registry_group)** :  This module leverages the group representation and group kind functionality provided by the **G2P Registry: Group** module. It integrates with group forms to display the calculated PMT score.

3. **[spp_custom_fields_ui](spp_custom_fields_ui)** :  The **spp_pmt** module relies on the **OpenSPP: Custom Fields UI** module to enable the configuration of PMT-specific criteria.  This integration allows administrators to define which custom fields are relevant to the PMT calculation and assign weights to these fields based on their relative importance.

4. **[spp_area](spp_area)** : This module integrates with the **OpenSPP Area** module to factor in geographical variations in the PMT calculation. This allows for more nuanced and context-specific assessments, recognizing that certain criteria may have varying weights depending on the location.

## Additional Functionality

* **PMT Calculation Logic**:  Introduces the core logic for calculating the PMT score. This logic takes into account the following:
    * **Group Memberships**:  Identifies all individuals belonging to a particular group.
    * **Custom Field Weights**:  Retrieves the weights assigned to relevant custom fields, as defined in the **[spp_custom_fields_ui](spp_custom_fields_ui)** module.
    * **Area-Specific Weights**:  Factors in any geographical variations in the weights assigned to custom fields, using data from the **[spp_area](spp_area)** module. 
    * **Score Aggregation**:  Calculates a weighted average of the relevant criteria for each individual within a group, then aggregates these individual scores to determine the overall PMT score for the group.

* **PMT Score Display**:  Extends the group view in the **[g2p_registry_group](g2p_registry_group)** module to display the calculated PMT score for each group. This allows users to quickly assess the relative need of different groups based on the defined PMT criteria.

* **Customizable Criteria**:
    * Leverages the flexibility of the **[spp_custom_fields_ui](spp_custom_fields_ui)** module to enable administrators to define and configure the criteria used in the PMT calculation. 
    * Allows for the inclusion of both individual-level and group-level custom fields in the calculation, providing a comprehensive assessment.

## Conclusion

The **OpenSPP Proxy Means Testing (spp_pmt)** module adds a valuable tool for targeting and prioritizing beneficiaries in social protection programs.  By integrating seamlessly with other OpenSPP modules, it leverages existing registry data and customizable configuration options to provide a flexible and context-specific PMT calculation. 
