# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Custom Field Recompute Daily",
    "summary": "Enables daily recomputation of specified fields to maintain data accuracy and improve performance by offloading intensive calculations.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": ["base_setup", "queue_job"],
    "data": [
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/ir_model_fields_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
