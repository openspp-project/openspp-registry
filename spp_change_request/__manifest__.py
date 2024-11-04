# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Change Request",
    "summary": "Streamlines the process of handling changes to registrant information within the OpenSPP system, providing a structured framework for submitting, reviewing, approving, and applying modifications.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {
        "python": [
            "python-magic",
        ]
    },
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_service_points",
        "spp_area",
        "spp_scan_id_document",
        "spp_dms",
        # "dms_field",
    ],
    "data": [
        "security/change_request_security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "data/mail_activity.xml",
        "data/dms.xml",
        "wizard/confirm_user_assignment_view.xml",
        "wizard/reject_change_request_view.xml",
        "wizard/cancel_change_request_view.xml",
        "views/main_view.xml",
        "views/change_request_view.xml",
        "views/change_request_validation_sequence_view.xml",
        "views/dms_file_view.xml",
        "views/registrant_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_change_request/static/src/scss/change_request.scss",
            # will be obsolete once the DMS for change request is developed
            # "spp_change_request/static/src/js/dms_preview.js",
        ],
        "web.assets_qweb": {
            "/spp_change_request/static/src/xml/dms_preview_widget.xml",
        },
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
