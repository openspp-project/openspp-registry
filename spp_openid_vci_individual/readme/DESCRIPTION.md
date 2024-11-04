# OpenSPP OpenID VCI Individual

This module extends the OpenSPP platform's Verifiable Credentials (VC) capabilities to specifically handle VC issuance for **individual registrants**. It seamlessly integrates the OpenID Connect for Verifiable Presentations (OpenID4VP) and Decentralized Identifiers (DIDs) framework with individual registrant data managed within the OpenSPP system.

## Purpose

The `spp_openid_vci_individual` module aims to:

- **Bridge Individual Data with VCs:**  Connect the VC issuance process directly to individual registrant profiles, allowing for the generation of VCs containing individual-specific attributes.
- **Streamline Issuance for Individuals:**  Provide a simplified and dedicated interface within the individual registrant profile for issuing VCs, enhancing user experience.

## Module Dependencies and Integration

1. **[spp_openid_vci](spp_openid_vci)**: This module inherits core functionalities from [spp_openid_vci](spp_openid_vci`](`spp_openid_vci`](`spp_openid_vci)**: This module inherits core functionalities from [`spp_openid_vci`), including:
   - **VCI Issuer Management:** Leverages the existing infrastructure for managing VCI issuers and their configurations.
   - **VC Generation and Signing:** Relies on the parent module's capabilities to generate, sign, and encode VCs based on defined templates and fetched registrant data.
   - **QR Code Generation:** Utilizes the same QR code generation mechanism to visually represent issued VCs for individuals.

2. **[g2p_registry_individual](g2p_registry_individual)**: This module integrates with the individual registry to access and utilize individual-specific data, such as:
   - **Individual Attributes:** Fetches data fields like full name, birthdate, gender, and other relevant attributes from the individual's registry profile to populate the claims within the VC.
   - **Issuance Interface:** Extends the individual registrant's profile view to include an "Issue Card" button, providing a direct and contextual point for VC issuance. 

## Additional Functionality

This module enhances the VC issuance process for individuals by:

- **Contextual Issuance Button:** Introduces an "Issue Card" button directly within the individual registrant's profile view in the registry, making the issuance process more intuitive and user-friendly.
- **Seamless Data Flow:** Automatically retrieves the necessary individual-specific attributes from the [g2p_registry_individual](g2p_registry_individual) module during VC generation, streamlining the issuance workflow.

## Example Usage Scenario

1. An administrator configures a VCI issuer within the [spp_openid_vci](spp_openid_vci) module, defining the format and data fields for a "Proof of Identity" VC intended for individual registrants. 
2. A user navigates to an individual's profile within the OpenSPP registry.
3. The user clicks the "Issue Card" button, which initiates the VC issuance process using the pre-configured "Proof of Identity" template.
4. The module automatically fetches the individual's name, birthdate, and other relevant attributes from the [g2p_registry_individual](g2p_registry_individual) data.
5.  A VC containing the individual's information is generated, signed, and encoded into a QR code, ready for display on a digital card or printed ID. 

## Conclusion

The `spp_openid_vci_individual` module simplifies the issuance and management of Verifiable Credentials for individual registrants within the OpenSPP ecosystem. By tightly integrating with the VC infrastructure and individual registry, it empowers organizations to extend the benefits of verifiable credentials to individuals, enhancing trust and streamlining identity verification processes. 
