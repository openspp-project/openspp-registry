# OpenSPP Base Demo

This module provides demonstration data for the OpenSPP system. It populates the database with sample records for various entities, allowing users to explore the system's functionalities with pre-populated data.

## Purpose

The primary purpose of the **[spp_base_demo](spp_base_demo)** module is to:

* **Provide realistic sample data:**  Offers a pre-configured dataset that mimics real-world scenarios, enabling users to interact with the system as if it were managing actual social protection programs and registries.
* **Facilitate user training and exploration:** Allows new users to familiarize themselves with the system's interface, data structures, and workflows without having to manually create large amounts of test data.
* **Showcase system capabilities:** Demonstrates the potential of OpenSPP by illustrating how different modules interact and how data flows through the system.

## Module Dependencies and Integration

* **[g2p_registry_base](g2p_registry_base)** (G2P Registry: Base):  Utilizes the base registry module to populate the system with sample registrant data, including individuals and potentially groups.
* **[g2p_programs](g2p_programs)** (G2P Programs):  Leverages the programs module to create demo programs, define eligibility criteria, and potentially simulate program cycles and beneficiary enrollment.
* **[product](product)** (Products): Utilizes the product module to create sample products, potentially representing goods or services distributed through social protection programs. 
* **[stock](stock)** (Inventory):  May potentially integrate with the inventory module to manage and track the stock levels of goods related to program benefits.

## Additional Functionality and Data Examples

The **[spp_base_demo](spp_base_demo)** module includes data files that populate the database with sample records for various entities. Here are some examples:

* **Users Data (data/users_data.xml):**  Creates demo user accounts with different roles and permissions, allowing users to explore the system from various perspectives.
* **Gender Data (data/gender_data.xml):** Defines common gender options used for registrant demographic information. 
* **Product Data (data/product_data.xml):**  Creates sample product records, potentially categorized by type, to represent goods distributed through programs.

## Conclusion

The **[spp_base_demo](spp_base_demo)** module serves as a valuable tool for users, implementers, and trainers to understand and explore the OpenSPP platform's capabilities. By providing realistic demo data, the module accelerates the learning curve and allows users to experience the system's full potential firsthand. 
