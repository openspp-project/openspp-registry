# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Area Management",
    "summary": "This module enables management of geographical areas, linking them to registrants for targeted interventions and analysis in social protection programs.",
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
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "queue_job",
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
        ]
    },
    "data": [
        "data/area_kind_data.xml",
        "data/queue_job_channel.xml",
        "security/ir.model.access.csv",
        "views/individual_views.xml",
        "views/group_views.xml",
        "views/area.xml",
        "views/area_kind.xml",
        "views/area_import_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
