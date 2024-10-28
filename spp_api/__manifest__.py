# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP API",
    "summary": "Provides a framework for building and managing a RESTful API for the OpenSPP platform, including API definition, documentation, security, and logging.",
    "category": "OpenSPP",
    "images": [
        "images/icon.png",
    ],
    "version": "17.0.1.3.0",
    "application": False,
    "author": "OpenSPP.org",
    "development_status": "Production/Stable",
    "maintainers": [
        "jeremi",
        "gonzalesedwin1123",
        "reichie020212",
    ],
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "spp_base_api",
        "spp_oauth",
        "web",
    ],
    "external_dependencies": {"python": ["bravado_core", "swagger_spec_validator", "jsonschema"], "bin": []},
    "data": [
        "security/openapi_security.xml",
        "security/ir.model.access.csv",
        "security/res_users_token.xml",
        "views/openapi_view.xml",
        "views/openapi_template.xml",
        "views/res_users_view.xml",
        "views/ir_model_view.xml",
        "views/spp_api_field_alias_views.xml",
        "wizards/res_users_bearer_token_views.xml",
    ],
    "demo": [
        "demo/openapi_demo.xml",
        "demo/openapi_security_demo.xml",
    ],
    "post_load": "post_load",
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
