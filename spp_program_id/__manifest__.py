# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Program ID",
    "summary": "Generates and manages unique IDs for social protection programs, enhancing identification and integration within the OpenSPP platform.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": [
        "spp_programs",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "views/g2p_program_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
