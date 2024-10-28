# OpenSPP OpenID VCI

## Overview

The [spp_openid_vci](spp_openid_vci.md) module enhances the functionality of the OpenSPP platform by enabling the issuance of Verifiable Credentials (VCs) to registrants. These VCs, based on OpenID Connect for Verifiable Presentations (OpenID4VP) and Decentralized Identifiers (DIDs), provide a secure and verifiable way to represent claims about a registrant's identity or attributes. 

This module builds upon the capabilities provided by several other modules, including [spp_encryption](spp_encryption.md), [g2p_openid_vci](g2p_openid_vci.md), [g2p_registry_base](g2p_registry_base.md), and [g2p_encryption_rest_api](g2p_encryption_rest_api.md), to offer a comprehensive VC issuance solution. 

## Purpose

This module aims to:

- **Issue Verifiable Credentials:** Generate and issue standardized VCs containing information drawn from the registry data. 
- **Generate QR Codes:**  Create scannable QR codes that encode the issued VCs, allowing for easy verification using mobile devices.
- **Provide a User Interface:** Offer an intuitive interface within the OpenSPP backend for managing VCI issuers and issuing VCs to registrants.

## Role and Integration

The [spp_openid_vci](spp_openid_vci.md) module relies on the foundational elements provided by its dependencies:

- **[spp_encryption](spp_encryption.md):** Leverages this module to digitally sign issued VCs, ensuring their authenticity and integrity.
- **[g2p_openid_vci](g2p_openid_vci.md):**  Utilizes the core VC issuance logic and issuer management functionalities provided by this module.
- **[g2p_registry_base](g2p_registry_base.md):**  Fetches the necessary registrant data (name, address, etc.) from this module to populate the claims within the VCs.
- **[g2p_encryption_rest_api](g2p_encryption_rest_api.md):** This module is not directly utilized by [spp_openid_vci](spp_openid_vci.md) but is essential for external systems to interact with the encryption and VC verification mechanisms.

## Additional Functionality

This module extends the capabilities of its dependencies by adding:

- **VC QR Code Generation:**  It generates and stores QR code representations of issued VCs, directly associating them with registrant records. 
- **ID Card Template:** Includes a customizable ID card template that incorporates the VC QR code, providing a tangible representation of a registrant's verifiable credentials. 
- **Issuance Wizard:** Introduces a user-friendly wizard within the registrant's profile to guide the VC issuance process. This wizard allows users to select the appropriate VCI issuer and generate the VC and corresponding QR code.

## Example Usage Scenario:

1. **Configuration:**  An administrator configures a VCI issuer within the [g2p_openid_vci](g2p_openid_vci.md) module to represent their organization and defines the format and data fields for the VC, including the scope of the credential (e.g., proof of address).
2. **Data Fetching:** When a user initiates the VC issuance process for a registrant, the module retrieves the relevant information from the registrant's profile managed by [g2p_registry_base](g2p_registry_base.md).
3. **VC Generation and Signing:** The module leverages the [g2p_openid_vci](g2p_openid_vci.md) module to construct the VC, populating it with the fetched data. The VC is then digitally signed using the encryption provider configured in the [spp_encryption](spp_encryption.md) module.
4. **QR Code Generation:** A QR code, encoding the signed VC, is generated. This QR code is then associated with the registrant's record.
5. **ID Card Printing (Optional):** Users can opt to print an ID card for the registrant, which includes the generated QR code. This provides a physical credential that can be easily verified using a QR code scanner.

## Conclusion

The [spp_openid_vci](spp_openid_vci) module enhances OpenSPP by providing a streamlined and user-friendly way to issue and manage Verifiable Credentials. By integrating seamlessly with other key modules, it enables organizations to leverage the power of VCs to enhance trust and streamline data sharing within their ecosystems and with external parties. 
