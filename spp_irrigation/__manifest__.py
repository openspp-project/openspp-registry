# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Irrigation",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "spp_base_gis",
    ],
    "data": [
        "security/irrigation_security.xml",
        "security/ir.model.access.csv",
        "views/irrigation_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Provides tools for managing and visualizing irrigation infrastructure within OpenSPP, enabling efficient tracking, planning, and analysis of irrigation systems and their impact.",
}
