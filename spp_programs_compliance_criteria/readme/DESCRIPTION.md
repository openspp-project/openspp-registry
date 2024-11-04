# OpenSPP Programs: Compliance Criteria

This document describes the **OpenSPP Programs: Compliance Criteria** module, an extension to the OpenSPP framework. This module adds functionality to manage compliance criteria within social protection programs. 

## Purpose

The **OpenSPP Programs: Compliance Criteria** module allows program administrators to define and enforce additional eligibility requirements beyond the initial criteria defined in the [g2p_programs](g2p_programs) module. This ensures that beneficiaries continuously meet specific conditions throughout their program participation. 

## Module Dependencies and Integration

1. [g2p_registry_base](g2p_registry_base): Leverages basic registrant information and relationships defined in the base registry module.

2. [g2p_programs](g2p_programs): 
    * Extends the program management features by introducing compliance managers and actions related to compliance checks. 
    * Integrates with program cycles to apply compliance filtering during beneficiary enrollment and cycle management.

3. [spp_area](spp_area): Utilizes geographical area information to define compliance criteria based on a beneficiary's location.

4. [spp_programs](spp_programs): Works in conjunction with the OpenSPP Programs module to apply compliance criteria to both cash and in-kind programs.

5. [spp_eligibility_sql](spp_eligibility_sql): Integrates with the SQL-based eligibility manager to allow for complex, dynamic compliance criteria based on SQL queries.

6. [spp_eligibility_tags](spp_eligibility_tags): Utilizes tag-based eligibility rules as potential compliance criteria, adding another layer of flexibility.

## Additional Functionality

* **Compliance Managers (spp.compliance.manager)**: A new model that links to specific eligibility managers (SQL-based, Tag-based, etc.) and defines them as compliance criteria for a program. 
* **Program Compliance Configuration (g2p.program)**: Extends the program model to include a list of compliance managers, defining the specific criteria that beneficiaries must meet.
* **Cycle-level Compliance Filtering (g2p.cycle)**: Adds actions to program cycles, allowing administrators to trigger compliance checks and filter beneficiaries accordingly. 
* **Automated Compliance Verification**: Provides configurable options to automate compliance checks:
    * **On Cycle Membership Creation**:  Automatically verifies compliance when a registrant is initially added to a program cycle.
    * **On Entitlement Creation**:  Verifies compliance before an entitlement is generated for a beneficiary.
* **Beneficiary State Management**:  Transitions beneficiaries between 'enrolled' and 'paused' states within a program cycle based on their compliance status.

## Conclusion

The **OpenSPP Programs: Compliance Criteria** module adds a crucial layer of control and flexibility to program management within OpenSPP. By allowing administrators to define and enforce ongoing compliance criteria, it ensures program integrity, targets benefits more effectively, and strengthens accountability within social protection programs. 
