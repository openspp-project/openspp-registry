# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Dashboard: Base",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["reichie020212"],
    "depends": [
        "base",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "spp_dashboard_base/static/src/dashboard/**/*",
            "spp_dashboard_base/static/src/chart/**/*",
            "spp_dashboard_base/static/src/card_board/**/*",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
