# OpenSPP Registry: Scan ID Document

This document outlines the functionality of the **OpenSPP Registry - Scan ID Document** module. This module enhances the registrant registration process by enabling users to scan physical ID documents directly into a registrant's profile. 

## Purpose

The **OpenSPP Registry - Scan ID Document** module aims to:

* **Streamline data entry:** Eliminate the need for manual input of ID document details, reducing errors and saving time.
* **Improve data accuracy:** Capture information directly from the source, ensuring the fidelity of ID data.
* **Enhance user experience:** Provide a convenient and intuitive way for users to associate scanned ID documents with registrant records. 

## Module Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base):** Utilizes the base registrant model to store and manage the scanned ID document data.
2. **[g2p_registry_individual](g2p_registry_individual):** Integrates with the individual registrant form to provide a seamless document scanning experience. 

## Additional Functionality

* **ID Document Scanning Widget:** Introduces a new widget ("id_document_reader") on the individual registrant form. This widget allows users to initiate the scanning process for physical ID documents. 
* **Data Extraction and Storage:**  Upon scanning, the module extracts relevant information from the ID document, such as name, date of birth, and ID number. This extracted data is then automatically populated into the corresponding fields within the registrant's profile. 
* **Document Image Storage:** The scanned ID document is stored as an image file linked to the registrant's record, allowing for future reference and verification.

## User Interface Changes

The module adds a new button labeled "Scan Document" to the individual registrant form. Clicking this button activates the ID document scanning widget, enabling users to scan physical documents directly into the system.
