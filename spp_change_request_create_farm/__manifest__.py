{
    "name": "OpenSPP Change Request: Create Farm",
    "summary": "Provides a specialized workflow for adding new farm in the registry.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_change_request",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_service_points",
        "spp_idpass",
        "spp_farmer_registry_base",
    ],
    "excludes": [
        "spp_change_request_create_group",
    ],
    "data": [
        "security/change_request_security.xml",
        "security/ir.model.access.csv",
        "data/dms.xml",
        "data/change_request_stage.xml",
        "data/change_request_sequence.xml",
        "data/change_request_target.xml",
        "views/change_request_create_farm_view.xml",
        "views/dms_file_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
