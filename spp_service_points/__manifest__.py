# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Service Points Management",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": "1",
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": [
        "jeremi",
        "gonzalesedwin1123",
    ],
    "depends": [
        "g2p_registry_base",
        "phone_validation",
        "spp_area",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security_group.xml",
        "views/main_view.xml",
        "views/group_views.xml",
        "views/service_points_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "This module enables the management of service points, linking them to geographical areas, company entities, and user accounts for streamlined service delivery within OpenSPP.",
}
