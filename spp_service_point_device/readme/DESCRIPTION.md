# OpenSPP Service Point Device

This document outlines the **OpenSPP Service Point Device** module, which extends the functionality of the **[spp_service_points](spp_service_points)** module to manage terminal devices associated with each service point. It allows for the registration and tracking of devices used at service points, including their model, Android version, and active status.

## Purpose

The **OpenSPP Service Point Device** module aims to:

* **Track Terminal Devices:**  Maintain a record of all terminal devices used at each service point within the OpenSPP system.
* **Manage Device Information:** Store relevant details about each device, such as the model, Android version, and a unique external identifier.
* **Monitor Device Status:** Track the active status of devices to identify and manage any inactive or unavailable devices.
* **Integrate with Service Points:** Seamlessly connect device information to its corresponding service point for centralized management and reporting.

## Dependencies and Integration

1. **[spp_service_points](spp_service_points)**: This module directly builds upon the **OpenSPP Service Points** module. It utilizes the `spp.service.point` model to link devices to their respective service points using the `service_point_id` field.

## Additional Functionality

* **Device Management (spp.service.point.device):**
    * Introduces a new model (`spp.service.point.device`) specifically for managing terminal device information.
    * Provides fields to capture device-specific details like model, Android version, external identifier, and active status.
    * Enables users to activate or deactivate devices and provides a visual indicator of their status.

* **Service Point Integration:**
    * Extends the `spp.service.point` model with a new button to access and manage the associated terminal devices.
    * Offers a dedicated view to list and manage all devices linked to a specific service point.

## Conclusion

The **OpenSPP Service Point Device** module enhances the OpenSPP system by providing a structured way to manage and monitor terminal devices deployed at various service points. By centralizing device information and linking it to service points, this module contributes to better hardware resource management and supports the efficient operation of social protection programs and farmer registries. 
