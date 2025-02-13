=====================================
OpenSPP Programs: Compliance Criteria
=====================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:f985b7759b6970c3a96f71515efde246424d9c2ea332f43487088deed34d14d5
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Alpha-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alpha
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_programs_compliance_criteria
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP Programs: Compliance Criteria
=====================================

This document describes the **OpenSPP Programs: Compliance Criteria**
module, an extension to the OpenSPP framework. This module adds
functionality to manage compliance criteria within social protection
programs.

Purpose
-------

The **OpenSPP Programs: Compliance Criteria** module allows program
administrators to define and enforce additional eligibility requirements
beyond the initial criteria defined in the
`g2p_programs <g2p_programs>`__ module. This ensures that beneficiaries
continuously meet specific conditions throughout their program
participation.

Module Dependencies and Integration
-----------------------------------

1. `g2p_registry_base <g2p_registry_base>`__: Leverages basic registrant
   information and relationships defined in the base registry module.

2. `g2p_programs <g2p_programs>`__:

   -  Extends the program management features by introducing compliance
      managers and actions related to compliance checks.
   -  Integrates with program cycles to apply compliance filtering
      during beneficiary enrollment and cycle management.

3. `spp_area <spp_area>`__: Utilizes geographical area information to
   define compliance criteria based on a beneficiary's location.

4. `spp_programs <spp_programs>`__: Works in conjunction with the
   OpenSPP Programs module to apply compliance criteria to both cash and
   in-kind programs.

5. `spp_eligibility_sql <spp_eligibility_sql>`__: Integrates with the
   SQL-based eligibility manager to allow for complex, dynamic
   compliance criteria based on SQL queries.

6. `spp_eligibility_tags <spp_eligibility_tags>`__: Utilizes tag-based
   eligibility rules as potential compliance criteria, adding another
   layer of flexibility.

Additional Functionality
------------------------

-  **Compliance Managers (spp.compliance.manager)**: A new model that
   links to specific eligibility managers (SQL-based, Tag-based, etc.)
   and defines them as compliance criteria for a program.
-  **Program Compliance Configuration (g2p.program)**: Extends the
   program model to include a list of compliance managers, defining the
   specific criteria that beneficiaries must meet.
-  **Cycle-level Compliance Filtering (g2p.cycle)**: Adds actions to
   program cycles, allowing administrators to trigger compliance checks
   and filter beneficiaries accordingly.
-  **Automated Compliance Verification**: Provides configurable options
   to automate compliance checks:

   -  **On Cycle Membership Creation**: Automatically verifies
      compliance when a registrant is initially added to a program
      cycle.
   -  **On Entitlement Creation**: Verifies compliance before an
      entitlement is generated for a beneficiary.

-  **Beneficiary State Management**: Transitions beneficiaries between
   'enrolled' and 'paused' states within a program cycle based on their
   compliance status.

Conclusion
----------

The **OpenSPP Programs: Compliance Criteria** module adds a crucial
layer of control and flexibility to program management within OpenSPP.
By allowing administrators to define and enforce ongoing compliance
criteria, it ensures program integrity, targets benefits more
effectively, and strengthens accountability within social protection
programs.

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
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_programs_compliance_criteria%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_programs_compliance_criteria>`_ project on GitHub.

You are welcome to contribute.
