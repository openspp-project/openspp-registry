# OpenSPP Data Export

## Overview

The PDS Data Export module enhances the functionality of the OpenSPP by providing a robust mechanism for exporting large datasets to Excel (.xlsx) format. This module directly addresses the limitations of Odoo's default export functionality when dealing with datasets exceeding the row limit of Excel 2007-2013 format (1,048,576 rows). 

## Purpose and Functionality

This module overrides the default `/web/export/xlsx` route, intercepting export requests and performing a pre-emptive check on the number of records to be exported. 

**Key features:**

* **Prevents system overload:** By calculating the number of records before generating the Excel report, the module prevents potential server timeouts and crashes that can occur when attempting to export excessively large datasets.
* **User-friendly error handling:**  If the record count exceeds the Excel row limit, the module raises a user-friendly error message, informing the user about the limitation and advising them to split the export into smaller chunks.
* **Seamless integration:**  The module seamlessly integrates with existing export functionalities, requiring no changes to user workflows. 

## Dependencies

* **web:** This module extends the core "web" module of Odoo, specifically overriding the default Excel export controller.

## Benefits

* **Improved system stability:**  Prevents server crashes due to large exports.
* **Enhanced user experience:** Provides clear error messages and guidance for managing large exports.
* **Data accessibility:** Ensures that users can reliably export data, even for large datasets. 
