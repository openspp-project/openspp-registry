# OpenSPP Demo

The `spp_demo` module serves as a demonstration and testing ground for the OpenSPP system, showcasing its capabilities with pre-populated data. It builds upon core OpenSPP modules to create a realistic simulation of social protection programs and registries in action.

## Purpose

* **Illustrate OpenSPP Functionality:** The module provides tangible examples of how various OpenSPP components work together, demonstrating data flow and interactions between modules.
* **Facilitate User Exploration:**  Pre-populated data allows users to explore the system's interface, features, and data structures without manually creating extensive test data. 
* **Accelerate Training:**  The demo module serves as a valuable tool for training users on OpenSPP, providing a controlled environment to practice workflows and tasks. 

## Dependencies and Integration

The `spp_demo` module relies heavily on the following OpenSPP modules:

* [theme_openspp_muk](theme_openspp_muk)  Applies a specific visual theme to the OpenSPP user interface for demonstration purposes.
* [g2p_registry_membership](g2p_registry_membership) (G2P Registry: Membership): Utilizes this module to establish and demonstrate relationships between individual and group registrants.
* [spp_custom_field](spp_custom_field) (OpenSPP Custom Field): Leverages this module to create and showcase custom fields added to registrant profiles, illustrating the flexibility of OpenSPP in capturing program-specific data.
* [queue_job](queue_job) (Queue Job):  Employs the Queue Job module to handle background tasks, demonstrating asynchronous processing for operations like data generation and potentially eligibility checks.
* [g2p_registry_individual](g2p_registry_individual) (G2P Registry: Individual):  Relies on this module to populate the system with sample individual registrant data.
* [spp_area](spp_area) (OpenSPP Area):  Integrates with this module to demonstrate the association of registrants and programs with geographical areas.
* [spp_custom_field_recompute_daily](spp_custom_field_recompute_daily) (OpenSPP Custom Field: Recompute Daily):  May utilize this module to showcase the automatic daily recomputation of specific custom fields, highlighting OpenSPP's ability to maintain up-to-date data. 
* [g2p_registry_base](g2p_registry_base) (G2P Registry: Base):  Builds upon the base registry module for core registrant management functionalities.
* [g2p_registry_group](g2p_registry_group) (G2P Registry: Groups): Leverages this module to create and manage sample groups of registrants.
* [spp_base_demo](spp_base_demo): This module provides basic demonstration data for the OpenSPP system, including users, gender options and products.
* [g2p_programs](g2p_programs) (G2P Programs):  Utilizes this module extensively to define and demonstrate social protection programs, eligibility criteria, program cycles, and potentially beneficiary enrollment and entitlement processes. 

## Additional Functionality 

* **Data Generation Utilities:**  The module includes Python scripts and functions within the `models/` directory to generate a variety of sample data, such as:
    * **Randomized Registrant Data:**  Creates individual and group registrants with realistic names, demographics, contact information, and relationships, often leveraging external libraries like `faker` for randomized data generation.
    * **Program Data:**  Generates demo programs with varying target types (individual, group), eligibility rules, and program cycles.  This may also include the creation of sample entitlements and payment records to simulate program activity. 
    * **Geographical Area Data:**  Populates the system with sample area hierarchies, linking registrants and programs to specific locations to demonstrate the geographical aspects of OpenSPP.

* **User Interface Integration:**  The module includes XML files within the `views/` directory that extend or modify the OpenSPP user interface, such as:
    * **Data Generation Actions:**  Adds buttons or menu items within relevant sections of the interface to trigger data generation scripts. This provides an easy way for users to populate the demo environment with sample data. 
    * **Custom Views:** May include custom views or modifications to existing views to highlight specific aspects of the demo data or showcase particular functionalities.  

## Conclusion

The `spp_demo` module is an essential component of the OpenSPP ecosystem for demonstration, testing, and training purposes. It provides a rich and interactive environment for users to explore the system's capabilities and understand how different modules work together to manage social protection programs and registries. 
