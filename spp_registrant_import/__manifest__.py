# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Registrant Import",
    "summary": "Streamlines the import of registrant data into OpenSPP, simplifies data mapping, and automates unique ID generation.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": [
        "base_import",
        "web",
        "spp_base",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/spp_area_views.xml",
        "views/spp_service_point_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_registrant_import/static/src/import_records/import_records.js",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
