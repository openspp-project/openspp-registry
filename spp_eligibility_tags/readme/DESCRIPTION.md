# OpenSPP Tag Based Eligibility Manager

This document outlines the functionality of the **OpenSPP Tag Based Eligibility Manager** module within the OpenSPP ecosystem. This module extends the eligibility management capabilities of OpenSPP, providing a flexible and efficient way to define eligibility criteria based on registrant tags and geographical areas.

## Purpose

The **OpenSPP Tag Based Eligibility Manager** module allows program administrators to:

* **Define eligibility rules using registrant tags:** Instead of manually selecting individual beneficiaries or relying solely on demographic data, programs can leverage the existing tagging system within OpenSPP to target specific groups of registrants based on shared characteristics, program participation history, or other relevant factors.
* **Incorporate geographical targeting:**  Administrators can further refine eligibility criteria by specifying geographical areas. This enables programs to target beneficiaries residing within specific districts or regions, enhancing the precision of program targeting and resource allocation. 
* **Simplify and automate eligibility verification:** By defining eligibility rules based on tags and areas, the module automates the process of identifying eligible beneficiaries. This reduces manual effort, minimizes errors, and ensures consistent application of eligibility criteria.

## Module Dependencies and Integration

1. **G2P Registry: Base ([g2p_registry_base](g2p_registry_base)(./g2p_registry_base.md))**:
    * Utilizes the tagging functionality of the base registry module to define eligibility rules based on registrant tags.
    * Leverages the geographical information associated with registrants, specifically their assigned areas, to apply area-based eligibility criteria.

2. **G2P Programs ([g2p_programs](g2p_programs)(./g2p_programs.md))**:
    * Extends the core program management module by introducing a new type of eligibility manager, the **Tag Based Eligibility Manager**.
    * Integrates seamlessly with existing program workflows, allowing administrators to select and configure the **Tag Based Eligibility Manager** for specific programs.

3. **OpenSPP Programs ([spp_programs](spp_programs)(./spp_programs.md))**: 
    * Leverages the functionality of the OpenSPP Programs module, particularly its handling of program memberships and beneficiary enrollment.
    * Ensures compatibility with both cash and in-kind entitlement programs, allowing for tag-based eligibility determination across different program types. 

## Additional Functionality

* **Tag Based Eligibility Manager Model (g2p.program_membership.manager.tags):** 
    * This model extends the base **Eligibility Manager** model within G2P Programs, introducing fields for selecting tags and areas to define eligibility criteria. 
    * Provides a user-friendly interface for administrators to configure tag-based eligibility rules, with clear visualization of the selected criteria.

* **Automated Eligibility Verification:**
    * When a program cycle is initiated, the **Tag Based Eligibility Manager** automatically identifies and flags registrants who meet the defined tag and area-based criteria as eligible.
    * This automated process streamlines beneficiary enrollment, saving time and ensuring accuracy in identifying qualified individuals or groups.

* **Dynamic Eligibility Updates:** 
    * As registrants' tags or area assignments change (e.g., due to data updates, program participation, or relocation), the module dynamically reassesses their eligibility status.
    * This ensures that eligibility remains current and reflects the most up-to-date information, minimizing instances of ineligible beneficiaries receiving benefits or eligible beneficiaries being excluded.

* **Improved Program Targeting and Efficiency:**
    * By leveraging tags and areas, programs can target specific segments of the population more effectively, ensuring that benefits reach the intended recipients.
    * This targeted approach enhances program impact and optimizes resource allocation by focusing on beneficiaries who are most likely to benefit from the program's interventions. 

## Conclusion

The **OpenSPP Tag Based Eligibility Manager** module empowers program implementers to define sophisticated eligibility criteria using a flexible and efficient tag-based approach. By seamlessly integrating with existing OpenSPP modules and automating key processes, it simplifies program administration, enhances targeting accuracy, and contributes to the overall effectiveness of social protection and agricultural support programs. 
