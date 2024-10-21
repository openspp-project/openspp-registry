# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Cycle: Attendance Compliance",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["reichie020212"],
    "depends": [
        "spp_programs_compliance_criteria",
        "spp_event_data",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/g2p_cycle_views.xml",
        "views/main_attendance_view.xml",
        "views/config_attendance_type_view.xml",
        "views/config_attendance_location_view.xml",
        "views/event_data_attendance_view.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {},
    "application": True,
    "installable": True,
    "auto_install": False,
}
