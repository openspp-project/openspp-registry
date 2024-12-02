# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Farmer Registry Default UI",
    "summary": "Provides UI for Farmer Registry Base.",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["reichie020212"],
    "depends": [
        "spp_farmer_registry_base",
    ],
    "excludes": [
        "spp_base",
    ],
    "data": [
        "views/group_view.xml",
        "views/individual_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
