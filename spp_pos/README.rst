===========
OpenSPP POS
===========

..
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:86cfba1ca834c2787b8bc99cd5b07c2deef87e9c4d004a12e01f9b068992960d
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_pos
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP POS
===========

This document details the **OpenSPP POS
(**\ `spp_pos <spp_pos>`__\ **)** module within the OpenSPP ecosystem.
This module extends the functionality of the Odoo Point of Sale (POS)
system to integrate with OpenSPP's core modules, enabling the redemption
of entitlements and management of beneficiary transactions at designated
points of sale.

Purpose
-------

The `spp_pos <spp_pos>`__ module bridges the gap between beneficiary
entitlements and their realization at physical or virtual points of
service. Its primary objectives are:

-  **Entitlement Redemption**: Allows beneficiaries to conveniently
   redeem their entitled benefits (e.g., cash transfers, in-kind goods)
   at POS terminals.
-  **Secure Identification**: Integrates with beneficiary identification
   mechanisms within OpenSPP to ensure secure and accurate transaction
   processing.
-  **Real-time Validation**: Verifies entitlement validity and
   beneficiary eligibility in real-time at the point of sale.
-  **Transaction Tracking**: Records all entitlement redemption
   transactions, linking them to specific beneficiaries, programs, and
   POS locations.
-  **Offline Capability**: Supports offline functionality to handle
   situations where internet connectivity is unreliable, ensuring
   service continuity.

Module Dependencies and Integration
-----------------------------------

1. **G2P Registry: Base
   (**\ `g2p_registry_base <g2p_registry_base>`__\ **)**:

   -  Relies on the base registry for accessing beneficiary data, such
      as unique identification details and active program participation.
      This information is essential for beneficiary authentication
      during POS transactions.

2. **Point of Sale (point_of_sale)**:

   -  Extends the core Odoo POS module with additional features tailored
      for social protection programs.
   -  Integrates seamlessly with the existing POS interface, minimizing
      disruptions to established workflows.

3. **G2P Programs (**\ `g2p_programs <g2p_programs>`__\ **)**:

   -  Interfaces with the G2P Programs module to retrieve and validate
      entitlement information.
   -  Utilizes entitlement data, including type, amount, validity
      period, and redemption status, to process transactions accurately.

4. **Product (product)**:

   -  Leverages the Product module to manage goods or services that can
      be redeemed using entitlements.
   -  Allows for flexible configuration of products specifically
      designated for social protection programs.

Additional Functionality
------------------------

-  **Entitlement Product Type**: Introduces a dedicated product type
   within Odoo to represent entitlements. This categorization
   distinguishes entitlement redemptions from regular product sales
   within the POS system.

-  **POS Interface Enhancements**: Extends the POS interface with
   specific features for entitlement redemption:

   -  **Beneficiary Identification**: Provides mechanisms for
      beneficiary authentication, such as scanning QR codes linked to
      their OpenSPP profiles or manual entry of identification details.
   -  **Entitlement Selection**: Displays available entitlements for the
      identified beneficiary, allowing POS operators to select and apply
      them to the transaction.
   -  **Real-time Validation**: Upon entitlement selection, the module
      communicates with the G2P Programs module to validate its
      authenticity, current status, and available balance.
   -  **Transaction Completion**: Processes the redemption, deducting
      the redeemed amount from the entitlement balance and generating a
      transaction record within both the POS and OpenSPP systems.

-  **Offline Mode Operations**: In scenarios with limited or no internet
   connectivity:

   -  The module enables offline transaction processing by storing
      entitlement data locally.
   -  Once connectivity is restored, offline transactions are
      synchronized with the central OpenSPP system, ensuring data
      consistency and accurate reporting.

Conclusion
----------

The `spp_pos <spp_pos>`__ module plays a crucial role in the OpenSPP
ecosystem by bridging the gap between entitled benefits and their
practical utilization. By integrating with core OpenSPP modules and
extending the Odoo POS system, it enables secure, transparent, and
efficient delivery of social protection benefits at designated points of
service. This integration streamlines the beneficiary experience while
providing program administrators with real-time visibility into program
utilization and impact.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_pos%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* OpenSPP.org

Maintainers
-----------

.. |maintainer-jeremi| image:: https://github.com/jeremi.png?size=40px
    :target: https://github.com/jeremi
    :alt: jeremi
.. |maintainer-gonzalesedwin1123| image:: https://github.com/gonzalesedwin1123.png?size=40px
    :target: https://github.com/gonzalesedwin1123
    :alt: gonzalesedwin1123

Current maintainers:

|maintainer-jeremi| |maintainer-gonzalesedwin1123|

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_pos>`_ project on GitHub.

You are welcome to contribute.
