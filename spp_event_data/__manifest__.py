# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Event Data",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": [
        "jeremi",
        "gonzalesedwin1123",
        "emjay0921",
    ],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_group",
        "g2p_registry_individual",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_data_view.xml",
        "views/registrant_view.xml",
        "wizard/create_event_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Records and tracks events related to individual and group registrants, providing a chronological history of changes and actions within the OpenSPP system.",
}
