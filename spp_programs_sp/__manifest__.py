{
    "name": "OpenSPP Programs: Service Points Integration",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_programs",
        "spp_programs",
        "spp_service_points",
        "spp_entitlement_cash",
        "spp_entitlement_in_kind",
    ],
    "data": [
        "wizard/create_program_wizard.xml",
        "views/programs_view.xml",
        "views/entitlements_view.xml",
        "views/service_point_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Extends OpenSPP Programs to integrate service points, enabling the association of beneficiaries and entitlements with designated service delivery locations for improved program efficiency and targeted benefit distribution.",
}
