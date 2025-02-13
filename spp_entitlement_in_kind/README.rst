===========================
OpenSPP In-Kind Entitlement
===========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:935bc20f824a58229ee0e3e9bcb79ca3e5151c10b6303905c8a262a31b942426
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Alpha-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alpha
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_entitlement_in_kind
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP In-Kind Entitlement
===========================

This document outlines the **OpenSPP In-Kind Entitlement
(**\ `spp_entitlement_in_kind <spp_entitlement_in_kind>`__\ **)**
module, which extends the OpenSPP platform to manage the distribution of
in-kind entitlements within social protection programs.

Purpose
-------

The `spp_entitlement_in_kind <spp_entitlement_in_kind>`__ module
enhances the existing `g2p_programs <g2p_programs>`__ **(Programs)**
module by introducing specific features and workflows for handling
in-kind entitlements, where beneficiaries receive goods or services
instead of cash transfers.

Role and Functionality
----------------------

This module builds upon the foundation established by its dependencies,
focusing specifically on in-kind entitlement management:

-  `g2p_registry_base <g2p_registry_base>`__ **(G2P Registry: Base)**:
   Utilizes the base registry to identify and manage beneficiary
   information.
-  `g2p_programs <g2p_programs>`__ **(G2P Programs)**: Extends the core
   program management features, leveraging existing program structures,
   cycles, and eligibility determination processes.
-  **Product (product)**: Leverages the product module to define the
   goods or services offered as in-kind entitlements.
-  **Stock (stock)**: Integrates with the stock module to manage
   inventory, track stock movements, and potentially trigger
   procurements based on approved entitlements.
-  `spp_service_points <spp_service_points>`__ **(OpenSPP Service
   Points)**: Allows for the designation of service points where
   beneficiaries can redeem their in-kind entitlements.
-  **Queue Job (queue_job)**: Employs the queue job framework to handle
   potentially resource-intensive operations, such as generating
   entitlements or updating inventory, asynchronously in the background.

Key Features
------------

1. **In-Kind Entitlement Definition:**

   -  Extends the ``g2p.entitlement.inkind`` model from
      `g2p_programs <g2p_programs>`__ to specifically manage in-kind
      entitlements.
   -  Links entitlements to products from the **Product** module,
      specifying the quantity a beneficiary is eligible to receive.
   -  Integrates with `spp_service_points <spp_service_points>`__ to
      associate entitlements with designated redemption locations.

2. **Entitlement Manager Extension:**

   -  Inherits from the ``g2p.program.entitlement.manager`` model in
      `g2p_programs <g2p_programs>`__.
   -  Introduces a new type of entitlement manager
      (``g2p.program.entitlement.manager.inkind``) designed for in-kind
      distributions.
   -  Allows configuration of inventory management options, linking to
      warehouses in the **Stock** module.
   -  Provides the ability to define complex entitlement rules based on
      beneficiary attributes, ensuring accurate allocation of goods or
      services.

3. **Inventory Management Integration:**

   -  When in-kind entitlements are approved, the module can trigger
      stock movements in the **Stock** module, transferring goods from
      designated warehouses to service points.
   -  Facilitates inventory tracking and reconciliation, ensuring
      transparency in the distribution process.

4. **Beneficiary Redemption:**

   -  While not directly handled by this module, it lays the groundwork
      for beneficiaries to redeem their entitlements at specified
      service points.
   -  Service points can use the existing **Stock** module functionality
      to record the outgoing delivery of goods to beneficiaries,
      completing the distribution cycle.

Benefits
--------

-  **Streamlined In-Kind Distribution:** Provides a structured approach
   to managing in-kind entitlements within existing social protection
   programs.
-  **Inventory Control:** Leverages Odoo's inventory management
   capabilities to track stock levels, movements, and potential
   procurement needs.
-  **Transparency and Accountability:** Enhances the transparency of
   in-kind distributions and facilitates accurate reporting on program
   operations.
-  **Improved Efficiency:** Automates key processes, such as entitlement
   generation and inventory updates, reducing manual effort and
   potential errors.

Conclusion
----------

The **OpenSPP In-Kind Entitlement
(**\ `spp_entitlement_in_kind <spp_entitlement_in_kind>`__\ **)** module
is a valuable addition to the OpenSPP platform, extending its
capabilities to effectively manage and track the distribution of in-kind
benefits. By integrating with core modules like **Stock** and
`spp_service_points <spp_service_points>`__ **(OpenSPP Service
Points)**, it provides a comprehensive solution for organizations
implementing programs that involve the delivery of goods or services to
beneficiaries.

.. IMPORTANT::
   This is an alpha version, the data model and design can change at any time without warning.
   Only for development or testing purpose, do not use in production.
   `More details on development status <https://odoo-community.org/page/development-status>`_

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_entitlement_in_kind%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_entitlement_in_kind>`_ project on GitHub.

You are welcome to contribute.
