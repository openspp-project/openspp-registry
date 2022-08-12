# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Photo",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_multi_image",
        "g2p_registry_base",
        # "spp_additional_data",
        "g2p_programs",
    ],
    "data": [
        "views/registrant.xml",
        "views/image.xml",
        "security/ir.model.access.csv",
        # "views/datasource.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
