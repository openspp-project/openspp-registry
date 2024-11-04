# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Event Data Program Membership",
    "summary": "This module allows users to record and track program membership-related events, such as enrollment, suspension, or exit, and link them to specific program membership records within OpenSPP.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["base", "spp_event_data", "g2p_programs"],
    "data": [
        "views/registrant_view.xml",
        "views/event_data_view.xml",
        "wizard/create_event_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
