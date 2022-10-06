# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Event Data - House Visit",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp-project/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": ["base", "spp_event_data"],
    "data": [
        "security/ir.model.access.csv",
        "views/house_visit_view.xml",
        "views/registrant_view.xml",
        "wizard/create_event_house_visit_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
