# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Hide Non-OpenSPP Menus",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "calendar", "contacts", "account", "event", "stock", "utm", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/hide_menu_data.xml",
        "views/hide_menu_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
