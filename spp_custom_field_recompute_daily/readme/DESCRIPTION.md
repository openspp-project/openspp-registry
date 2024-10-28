# OpenSPP Custom Field Recompute Daily

This module extends the functionality of OpenSPP by introducing a mechanism to recompute specific fields on a daily basis. This is particularly useful for maintaining up-to-date values for fields that are computationally intensive or rely on frequently changing data.

## Purpose

The primary goal of this module is to:

* **Enable daily recomputation of fields:**  Allow administrators to mark specific fields for daily recomputation.
* **Improve performance:** By offloading computationally expensive field calculations to a scheduled task, the module prevents performance bottlenecks during regular system operations.
* **Ensure data accuracy:**  Regular recomputation ensures that fields relying on dynamic data remain consistent and reflect the latest information.

## Functionality and Integration

### Integration with `queue_job`

This module leverages the `queue_job` module to handle the asynchronous recomputation of fields. When a field marked for "Daily Recompute" needs updating, the module creates a background job using `queue_job`. This approach prevents the recomputation process from impacting the system's responsiveness, especially when dealing with large datasets.

### Integration with `base_setup`

The module integrates with `base_setup` to provide configuration options for daily recomputation. Administrators can set the "Maximum Daily Recompute Records Count" through the "Settings" menu. This parameter limits the number of records processed synchronously during each recomputation cycle, preventing potential performance issues.

## Key Features

* **Field level configuration:** The module adds a "Daily Recompute" checkbox to the field definition in the Odoo interface. Enabling this option marks the field for daily recomputation.
* **Cron Job:** A scheduled task runs daily to trigger the recomputation of marked fields.
* **Performance optimization:** The recomputation process is designed to be asynchronous and utilizes the `queue_job` framework to minimize the impact on system performance.
* **Configuration options:** Administrators can define the maximum number of records to be recomputed synchronously, allowing for fine-tuning based on system capacity.

## Usage

1. **Enable "Daily Recompute":** In the Odoo interface, navigate to the technical settings of the desired model. Locate the field you want to recompute daily and enable the "Daily Recompute" option.
2. **Configure Recomputation Settings (Optional):**  Access the "Settings" menu and locate the "Daily Recomputing" section. Adjust the "Maximum Daily Recompute Records Count" based on your system's capacity and performance requirements.

Once configured, the module automatically handles the daily recomputation of the marked fields in the background. This ensures that your data remains consistent and up-to-date without impacting the performance of other system operations. 
