# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Area Management",
    "summary": "This module extends the OpenSPP Area (Base) module to include additional features for managing and organizing geographical areas within the system.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "spp_area_base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "queue_job",
    ],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "views/individual_views.xml",
        "views/group_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
