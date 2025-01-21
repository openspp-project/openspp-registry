# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP POS: ID Redemption",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "point_of_sale",
        "spp_pos",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_programs",
        "spp_entitlement_cash",
        "spp_area",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "spp_pos_id_redemption/static/src/view/popup_voucher.xml",
            "spp_pos_id_redemption/static/src/view/entitlement_product_list.xml",
            "spp_pos_id_redemption/static/src/view/product_screen.xml",
            "spp_pos_id_redemption/static/src/view/product_card.xml",
            "spp_pos_id_redemption/static/src/view/product_list.xml",
            "spp_pos_id_redemption/static/src/view/action_pad.xml",
            "spp_pos_id_redemption/static/src/view/partner_list.xml",
            "spp_pos_id_redemption/static/src/view/payment_screen.xml",
            "spp_pos_id_redemption/static/src/view/customer_note.xml",
            "spp_pos_id_redemption/static/src/view/ticket_screen.xml",
            "spp_pos_id_redemption/static/src/js/popup_voucher.js",
            "spp_pos_id_redemption/static/src/js/entitlement_product_list.js",
            "spp_pos_id_redemption/static/src/js/pos_store.js",
            "spp_pos_id_redemption/static/src/js/product_screen.js",
            "spp_pos_id_redemption/static/src/js/product_list.js",
            "spp_pos_id_redemption/static/src/js/payment_screen.js",
            "spp_pos_id_redemption/static/src/js/product_card.js",
            "spp_pos_id_redemption/static/src/js/partner_list.js",
            "spp_pos_id_redemption/static/src/js/db.js",
            "spp_pos_id_redemption/static/src/js/customer_note.js",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/registrant_view.xml",
        "views/product_template_view.xml",
        "views/entitlements_view.xml",
        "views/cycle_view.xml",
        "views/pos_view.xml",
        "views/pos_config_view.xml",
        "wizard/create_program_wizard.xml",
        "report/paper_format.xml",
        "report/id_barcode_printout.xml",
        "wizard/create_program_wizard.xml",
    ],
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
