# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Change Request Base",
    "summary": "Streamlines the process of handling changes to registrant information within the OpenSPP system, providing a structured framework for submitting, reviewing, approving, and applying modifications.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "external_dependencies": {},
    "depends": [
        "base",
        "spp_dms",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/change_request_security.xml",
        "data/sequences.xml",
        "data/mail_activity.xml",
        "wizard/confirm_user_assignment_view.xml",
        "wizard/reject_change_request_view.xml",
        "wizard/cancel_change_request_view.xml",
        "views/main_view.xml",
        "views/change_request_validation_sequence_view.xml",
        "views/dms_file_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_change_request_base/static/src/scss/change_request.scss",
        ],
        "web.assets_qweb": {
            "/spp_change_request_base/static/src/xml/dms_preview_widget.xml",
        },
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
