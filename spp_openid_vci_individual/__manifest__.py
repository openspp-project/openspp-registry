{
    "name": "OpenSPP OpenID VCI Individual",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["spp_openid_vci", "g2p_registry_individual"],
    "external_dependencies": {"python": ["qrcode"]},
    "data": ["views/individual_view.xml"],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    # odoo-upgrades
    "summary": "Enables the issuance of Verifiable Credentials (VCs) for individual registrants within the OpenSPP platform, integrating with OpenID Connect for Verifiable Presentations and Decentralized Identifiers.",
}
