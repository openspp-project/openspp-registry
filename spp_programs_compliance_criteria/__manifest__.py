# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs: Compliance Criteria",
    "summary": "Manages compliance criteria within social protection programs, allowing administrators to define and enforce additional eligibility requirements beyond initial program criteria.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_programs",
        "spp_area",
        "spp_programs",
        "spp_eligibility_sql",
        "spp_eligibility_tags",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/g2p_cycle_views.xml",
        "views/g2p_program_views.xml",
        "views/res_config_settings_views.xml",
        "views/cycle_membership_views.xml",
        "wizards/g2p_program_create_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_programs_compliance_criteria/static/src/js/field_domain.js",
            "spp_programs_compliance_criteria/static/src/xml/field_domain.xml",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
