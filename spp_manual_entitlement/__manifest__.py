# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Manual Entitlement",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "spp_registry",
        "g2p_programs",
        "spp_registrant_import",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/cycle_view.xml",
        "wizard/manual_entitlement_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Provides a mechanism for manually creating entitlements for beneficiaries within specific program cycles in OpenSPP, offering flexibility for programs with unique eligibility criteria or situations not covered by automated rules.",
}
