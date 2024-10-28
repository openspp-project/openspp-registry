# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Import Match",
    "summary": "Enhances data imports in OpenSPP by enabling the matching of imported records with existing data to prevent duplicates and ensure data integrity.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base", "base_import", "queue_job"],
    "data": [
        "data/queue_job_data.xml",
        "security/ir.model.access.csv",
        "views/import_match_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/spp_import_match/static/src/legacy/js/custom_base_import.js",
            "/spp_import_match/static/src/legacy/js/import_records.js",
        ],
        "web.assets_qweb": [
            "spp_import_match/static/src/legacy/xml/custom_base_import.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
