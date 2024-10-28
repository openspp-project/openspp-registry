# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Event Demo",
    "summary": "Provides demonstration data and functionalities for the OpenSPP event tracking system, showcasing practical applications through predefined event types, data models, views, and wizards.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": ["base", "spp_event_data"],
    "data": [
        "security/ir.model.access.csv",
        "views/house_visit_view.xml",
        "views/phone_survey_view.xml",
        "views/registrant_view.xml",
        "wizard/create_event_house_visit_wizard.xml",
        "wizard/create_event_phone_survey_wizard.xml",
        "wizard/create_event_school_enrolment_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
