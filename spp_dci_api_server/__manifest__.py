# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP DCI API Server",
    "summary": "Provides a DCI-compliant RESTful API for secure data exchange with OpenSPP's registry.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "author": "OpenSPP.org",
    "development_status": "Beta",
    "maintainers": [
        "jeremi",
        "gonzalesedwin1123",
        "reichie020212",
    ],
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "spp_oauth",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/client_credentials_view.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
