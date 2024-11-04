# OpenSPP Consent Module

## Overview

The OpenSPP Consent module enhances the functionality of the [g2p_registry_individual](g2p_registry_individual) and [g2p_registry_group](g2p_registry_group) modules by providing a framework for managing and tracking consents provided by registrants (both individuals and groups). This module is essential for ensuring compliance with data privacy regulations and maintaining ethical data management practices within social protection programs.

## Features

* **Consent Recording:** Allows authorized users to record consents obtained from registrants, specifying the type of consent, the signatory (for groups), and the expiry date.
* **Consent Management:** Provides a centralized repository for storing and managing all recorded consents, making it easy to track consent status and expiry dates.
* **Consent Integration:** Seamlessly integrates with the registrant profiles in the [g2p_registry_individual](g2p_registry_individual) and [g2p_registry_group](g2p_registry_group) modules, providing direct access to consent information from the registrant's record.
* **Expired Consent Tracking:** Includes a dedicated view for monitoring expired consents, enabling proactive management of consent renewals and ensuring continued compliance.

## Functionality and Integration

The OpenSPP Consent module introduces the following key elements:

* **Consent Configuration:** Defines different types of consents that can be recorded within the system. 
* **Consent Model:** Stores information related to each consent, including the type of consent, associated registrant (individual or group), signatory, expiry date, and related configuration.
* **Consent Mixin:** A mixin model that extends the functionality of the `res.partner` model (used for both individuals and groups) in the registry modules. This mixin adds a relationship field to link registrants with their respective consents.
* **Consent Wizard:** Provides a user-friendly interface for recording new consents, accessible directly from the registrant's profile.
* **Expired Consent View:** Offers a dedicated view for easily identifying and managing consents that have passed their expiry date.

## Benefits

* **Enhanced Data Privacy:** Ensures compliance with data privacy regulations by explicitly obtaining and tracking consents for data processing activities.
* **Improved Transparency:** Increases transparency by providing a clear record of consents obtained from registrants.
* **Streamlined Consent Management:** Simplifies the process of managing consents, reducing administrative burden and the risk of errors.
* **Proactive Compliance:** Enables proactive management of consents, ensuring timely renewals and minimizing the risk of non-compliance.

By integrating the OpenSPP Consent module with your existing registry system, you can significantly strengthen your data protection measures and promote ethical data management practices within your social protection programs.
