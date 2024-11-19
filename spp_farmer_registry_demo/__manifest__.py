# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Farmer Registry Demo",
    "summary": "Provides pre-populated demo data for the OpenSPP Farmer Registry, showcasing its features with realistic sample data.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "external_dependencies": {"python": ["faker"]},
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "g2p_registry_base",
        "spp_farmer_registry_base",
        "spp_farmer_registry_default_ui",
        "spp_base_demo",
        "queue_job",
        "spp_custom_filter_farmer_registry"
    ],
    "excludes": [
        "spp_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/asset_type_data.xml",
        "data/machinery_type_data.xml",
        "data/aqua_data.xml",
        "data/crop_data.xml",
        "data/livestock_data.xml",
        "data/chemical_data.xml",
        "data/fertilizer_data.xml",
        "data/feed_items_data.xml",
        "views/group_view.xml",
        "views/individual_view.xml",
        "views/generate_farmer_data_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
