# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Farmer Registry Dashboard",
    "summary": "Provides interactive dashboards and reports for visualizing data from the OpenSPP Farmer Registry, offering insights into key metrics and trends related to registered farmers.",
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
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_farmer_registry_base",
        "spp_farmer_registry_demo",
        "spreadsheet_dashboard",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/dashboards.xml",
        "reports/farmer_registry_report_views.xml",
        "views/main_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
