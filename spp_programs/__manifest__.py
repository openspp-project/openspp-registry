# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs",
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
        "web",
        "g2p_registry_base",
        "g2p_programs",
        "spp_area",
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/entitlement_view.xml",
        "views/entitlement_cash_view.xml",
        "views/cycle_view.xml",
        "views/programs_view.xml",
        "views/registrant_view.xml",
        "views/inkind_entitlement_report_view.xml",
        "views/managers/eligibility_manager_view.xml",
        "views/managers/entitlement_manager_view.xml",
        "wizard/inkind_entitlement_report_wiz.xml",
        "wizard/create_program_wizard.xml",
        "report/program_approval_receipt.xml",
        "report/report_format.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_programs/static/src/js/domain_field.js",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
