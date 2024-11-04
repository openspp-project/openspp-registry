{
    "name": "OpenSPP Import: DCI API",
    "summary": "Enables integration with external registries, particularly those adhering to the DCI (Digital Civil Identity) standard, for importing and synchronizing registrant data into OpenSPP.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "author": "OpenSPP.org",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_programs",
        "spp_programs",
        "g2p_registry_base",
        "g2p_registry_individual",
        "spp_registry_data_source",
    ],
    "data": [
        "security/fetch_crvs_security.xml",
        "security/ir.model.access.csv",
        "data/crvs_data_source.xml",
        "data/crvs_location_data.xml",
        "views/create_program_wizard_view.xml",
        "views/eligibility_manager_view.xml",
        "views/fetch_crvs_beneficiary_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # obsolete javascript
            "spp_import_dci_api/static/src/js/field_domain.js",
            "spp_import_dci_api/static/src/xml/field_domain.xml",
        ],
    },
    "application": True,
    "auto_install": False,
    "installable": True,
}
