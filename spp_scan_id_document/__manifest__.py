# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Registry: Scan ID Document",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["base", "g2p_registry_base", "g2p_registry_individual"],
    "data": ["views/registrant.xml"],
    "assets": {
        "web.assets_backend": [
            # web.AbstractField module is already obsolete in odoo 17
            "/spp_scan_id_document/static/src/js/registrant.js",
            "/spp_scan_id_document/static/src/xml/registrant_widget.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Enables the scanning of physical ID documents directly into a registrant's profile, streamlining data entry and improving accuracy in the OpenSPP Registry.",
}
