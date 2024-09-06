{
    "name": "OpenSPP Change Request: Add Farmer",
    "summary": "Provides a specialized workflow for adding new farmers to existing groups in the registry.",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_change_request",
        "spp_farmer_registry_base",
        "spp_registry",
        "spp_service_points",
        "spp_land_record",
    ],
    "data": [
        "security/change_request_security.xml",
        "security/ir.model.access.csv",
        "data/dms.xml",
        "data/change_request_stage.xml",
        "data/change_request_sequence.xml",
        "data/change_request_target.xml",
        "data/id_type.xml",
        "views/change_request_add_farmer_view.xml",
        "views/dms_file_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
