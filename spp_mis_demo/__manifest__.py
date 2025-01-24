# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Demo",
    "summary": "Provides demonstration data and functionalities for the OpenSPP system, showcasing its capabilities in managing social protection programs and registries with pre-populated data for exploration and testing.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_base_demo",
        "spp_base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "g2p_programs",
        "spp_custom_field",
        "spp_custom_field_recompute_daily",
        "spp_idpass",
        "spp_area",
        "theme_openspp_muk",
        # "spp_pos",
        # "spp_sms",
        "queue_job",
        "g2p_programs",
        "product",
        "stock",
        "spp_custom_filter_ui",
    ],
    "excludes": [
        "spp_farmer_registry_base",
    ],
    "external_dependencies": {"python": ["faker"]},
    "data": [
        "data/res_lang_data.xml",
        "data/product_data.xml",
        "security/ir.model.access.csv",
        "views/generate_data_view.xml",
        "views/generate_program_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
