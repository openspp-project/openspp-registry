# OpenSPP ID Queue

This document outlines the **OpenSPP ID Queue** module within the OpenSPP ecosystem.  This module adds functionality for managing requests for printed identification cards for registrants. It integrates with other OpenSPP modules to provide a seamless workflow from ID request to printing and distribution.

## Purpose

The **OpenSPP ID Queue** module is designed to:

* **Streamline ID Card Requests**:  Provide a structured process for users to request printed ID cards for registrants, including the ability to select specific ID card templates.
* **Implement Approval Workflows**:  Incorporate optional approval steps for ID card requests, ensuring that requests are reviewed and authorized before generation.
* **Facilitate Batch Printing**:  Group ID card requests into batches for efficient printing and distribution, especially for large-scale programs.
* **Track ID Card Status**:  Monitor the progress of ID card requests through various stages (new, approved, generating, printed, distributed), providing transparency and accountability. 

## Dependencies and Integration

1. **[g2p_registry_base](g2p_registry_base)** (G2P Registry: Base):  The ID Queue module relies on the **Registrant (res.partner)** model from the **G2P Registry: Base** module to identify and link ID card requests to specific registrants. 

2. **[spp_idpass](spp_idpass)** (OpenSPP ID PASS):  It integrates tightly with the **OpenSPP ID PASS** module, utilizing the predefined ID card templates and the ID generation mechanism.

3. **[queue_job](queue_job)** (Queue Job):  Leverages the **Queue Job** module for background processing of ID card generation, particularly when handling large batches, to avoid impacting system performance.

4. **[spp_area](spp_area)** (OpenSPP Area):  Integrates with the **OpenSPP Area** module to associate ID card requests with specific geographical areas, enabling location-based reporting and distribution management.

5. **[g2p_registry_group](g2p_registry_group)** (G2P Registry: Group): Incorporates functionality from the **G2P Registry: Group** module to support ID card requests and batch printing for groups of registrants.

## Additional Functionality

* **ID Request Queue (`spp.print.queue.id`)**:
    * Introduces a dedicated model to manage individual ID card requests, storing request details, associated registrant, selected template, request status, and approval information.
    * Provides functions to move requests through the workflow: approve, generate, print, distribute, and cancel.
    * Implements a messaging system to record actions taken on requests, enhancing auditability.

* **ID Print Batch (`spp.print.queue.batch`)**:
    * Enables the grouping of approved ID requests into batches for streamlined printing.
    * Offers functionalities to approve, generate, print, and mark batches as distributed.
    * Includes a status tracking system for batches, mirroring the individual request statuses.

* **Auto-Approve Configuration**:
    * Allows administrators to configure the system to automatically approve ID requests upon creation, potentially bypassing the manual approval step for specific workflows.

* **Registrant Integration**:
    * Extends the **Registrant (`res.partner`)** model to include a link to all associated ID card requests, providing a centralized view of a registrant's ID card history. 

## Conclusion

The **OpenSPP ID Queue** module enhances OpenSPP's ID card management capabilities by providing a structured and efficient system for handling ID card requests, approvals, batch printing, and distribution tracking.  Its integration with other core OpenSPP modules ensures a cohesive and streamlined experience for managing registrant identification within social protection programs and farmer registries. 
