# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Base",
    "category": "OpenSPP/OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "utm",
        "mail",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_area",
        "spp_idpass",
        "spp_idqueue",
        "spp_service_points",
        "spp_custom_field",
        "spp_custom_fields_ui",
        "spp_programs",
    ],
    "external_dependencies": {
        "python": ["fastapi==0.112.2", "extendable_pydantic==1.3.0", "numpy>=1.22.2", "urllib3>=2.2.2", "zipp>=3.19.1"]
    },  # not directly required, pinned by Snyk to avoid a vulnerability and for fastapi, compatibility issues.
    "data": [
        "security/ir.model.access.csv",
        "data/top_up_card.xml",
        "views/registrant_view.xml",
        "views/hide_menu_view.xml",
        "views/main_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Provides essential configurations, UI customizations, and base functionalities for the OpenSPP system, including top-up card management and integration with other OpenSPP modules for areas, service points, programs, and custom fields.",
}
