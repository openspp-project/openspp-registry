# OpenSPP OpenID VCI Group

## Overview

The `spp_openid_vci_group` module extends the functionality of the [spp_openid_vci](spp_openid_vci) module to enable the issuance of Verifiable Credentials (VCs) specifically for groups of registrants, building upon the group management capabilities provided by the [g2p_registry_group](g2p_registry_group) module to enable the issuance of Verifiable Credentials (VCs) specifically for groups of registrants, building upon the group management capabilities provided by the [g2p_registry_group](g2p_registry_group) module. This module leverages the existing VC issuance framework to provide a streamlined process for issuing VCs that represent a group's identity and attributes.

## Purpose

This module's primary purpose is to:

- **Issue Group-Specific VCs:**  Generate and issue VCs that contain information relevant to a registered group, such as the group's name, type, members, or other relevant attributes.
- **Integrate with Group Management:** Seamlessly integrate with the group management functionality provided by the [g2p_registry_group](g2p_registry_group) module, allowing users to issue VCs directly from a group's profile.

## Role and Integration

The `spp_openid_vci_group` module works in conjunction with the following modules:

- **[spp_openid_vci](spp_openid_vci):** Inherits the core VC issuance logic, issuer management, and QR code generation functionality from this module, ensuring consistency in the issuance process for both individuals and groups. 
- **[g2p_registry_group](g2p_registry_group):**  Fetches group-related data, such as group type and member information, to populate the claims within the VCs.  The module also integrates into the group profile view to provide a user-friendly way to issue VCs.

## Additional Functionality

- **Group VCI Issuer Type:** Introduces a new "GroupRegistry" issuer type within the VCI issuer settings, allowing administrators to configure issuers specifically for generating group-related VCs.
- **Group-Specific VC Issuance:** Modifies the VC issuance logic to accommodate group-related data, ensuring that the issued VCs contain information specific to the group, such as group name, type, and potentially a list of members.
- **Group Profile Integration:**  Adds a button to the group profile view within the [g2p_registry_group](g2p_registry_group) module to initiate the VC issuance process directly from the group's record.

## Example Usage Scenario

1. **Configuration:**  An administrator configures a VCI issuer with the type "GroupRegistry" and specifies the data fields for the group VC, including the group name, type, and any other relevant attributes.
2. **Data Retrieval:** When a user initiates the VC issuance process for a group, the module retrieves the necessary information from the group's record, including the group's name, type, and potentially a list of its members.
3. **VC Generation:** The module utilizes the inherited functionality from [spp_openid_vci](spp_openid_vci) to generate the VC, populating it with the retrieved group-specific data. The VC is then digitally signed to ensure its integrity. 
4. **QR Code Generation:** A QR code representing the issued VC is generated and associated with the group's record.
5. **Presentation on Group Profile:** The generated VC or its QR code representation can be displayed on the group's profile within the registry, allowing for easy access and verification.

## Conclusion

The `spp_openid_vci_group` module enhances OpenSPP's Verifiable Credential issuance capabilities by extending them to groups of registrants. It leverages the existing VC infrastructure and seamlessly integrates with the group management functionality to provide a streamlined process for issuing and managing group-specific VCs. This integration further strengthens OpenSPP's ability to provide secure and verifiable digital identities within its ecosystem, encompassing both individual and group-level representations. 
