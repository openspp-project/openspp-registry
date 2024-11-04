# OpenSPP Import Match

The [spp_import_match](spp_import_match) module enhances the data import functionality within OpenSPP by enabling the matching of imported records with existing records in the database. This helps prevent duplicate entries and ensures data integrity during import processes.

## Purpose

The primary goals of the [spp_import_match](spp_import_match) module are:

- **Prevent Duplicate Records:** Avoid creating duplicate entries for existing registrants or entities during data imports.
- **Improve Data Accuracy:**  Ensure that imported data is linked to the correct existing records, enhancing overall data quality.
- **Streamline Import Processes:** Provide a mechanism for automating record matching, reducing manual reconciliation efforts.

## Dependencies and Integration

1. **[queue_job](queue_job):** This module leverages the [queue_job](queue_job](queue_job](queue_job):** This module leverages the [queue_job) module to handle asynchronous import processes. This enables the processing of large datasets in the background, preventing system slowdowns.

2. **[g2p_registry_base](g2p_registry_base):**  The [spp_import_match](spp_import_match) module extends the functionality of the [g2p_registry_base](g2p_registry_base](g2p_registry_base](g2p_registry_base):**  The [spp_import_match](spp_import_match) module extends the functionality of the [g2p_registry_base) module. It specifically interacts with the models and functionalities related to managing registrant data and relationships.

3. **[base_import](base_import):** The core import functionality is inherited and extended from Odoo's built-in [base_import](base_import) module. [spp_import_match](base_import](spp_import_match](base_import):** The core import functionality is inherited and extended from Odoo's built-in [base_import](base_import) module. [spp_import_match) enhances this with capabilities for record matching during the import process.

## Functionality and Integration

* **Import Matching Rules (spp.import.match):**  This model defines the rules for matching imported data with existing records.  Users can define matching criteria based on various fields and conditions. 
    * It allows specifying which model to match against, ensuring the flexibility to work with different data types.
    * Users can set up multiple fields to match on, creating a robust system for identifying potential duplicates.
    * Conditional matching based on specific import values adds another layer of precision to the process.

* **Field Mapping (spp.import.match.fields):**  This model handles the mapping of fields between the imported data and the target model's fields.
    * It allows for matching on both simple fields and sub-fields within relational fields, supporting complex data structures. 
    * The module validates the uniqueness of fields chosen for matching, preventing configuration errors.

* **Integration with Data Import:** The module seamlessly integrates with the standard Odoo import process. During import, if matching rules are defined for the target model, the module attempts to find existing records that match the imported data.  This matching process is integrated into both standard imports and asynchronous imports handled by the [queue_job](queue_job) module.

* **Overwriting Existing Data:** The module provides an option to overwrite existing data with imported data when a match is found. This allows users to update existing records with new information from imports while still leveraging the matching capabilities to prevent duplicates.

## Workflow Example

1. **Define Matching Rules:** An administrator configures import matching rules for the `res.partner` model (used for registrants) in the `spp.import.match` model. They specify that matching should occur based on the "National ID Number" and "Date of Birth" fields.

2. **Import Data:**  A user initiates a data import for a list of potential beneficiaries. The import file includes fields for "National ID Number", "Date of Birth", and other relevant information.

3. **Record Matching:** During the import process, the [spp_import_match](spp_import_match) module utilizes the defined rules to compare the imported data with existing registrant records.  If a match is found based on the "National ID Number" and "Date of Birth," the module prevents the creation of a duplicate record.

4. **Data Update (Optional):**  If the "Overwrite Match" option is enabled in the matching rules, the module updates the existing registrant's record with any new information from the import file. 

## Conclusion

The [spp_import_match](spp_import_match) module significantly enhances data management within OpenSPP by providing a robust and configurable system for matching imported records with existing data. This contributes to a more accurate, reliable, and efficient data ecosystem for social protection programs. 
