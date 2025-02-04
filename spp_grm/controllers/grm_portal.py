import logging

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class SPPGrmPortal(CustomerPortal):
    @http.route(["/my/tickets", "/my/tickets/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_tickets(self, page=1, **kw):
        partner = request.env.user.partner_id
        ticket = request.env["spp.grm.ticket"]
        domain = [("partner_id", "=", partner.id)]

        # Pagination logic
        tickets = ticket.search(domain)
        values = {
            "tickets": tickets,
            "page_name": "tickets",
        }
        return request.render("spp_grm.portal_my_tickets", values)

    @http.route(["/my/ticket/new"], type="http", auth="user", website=True)
    def portal_ticket_new(self, **kw):
        categories = request.env["spp.grm.ticket.category"].search([])
        channels = request.env["spp.grm.ticket.channel"].search([])
        return request.render(
            "spp_grm.portal_create_ticket",
            {
                "categories": categories,
                "channels": channels,
                "page_name": "tickets",
                "ticket": "new",
            },
        )

    @http.route(["/my/ticket/submit"], type="http", auth="user", website=True, csrf=True)
    def portal_ticket_submit(self, **kw):
        partner = request.env.user.partner_id
        vals = {
            "name": kw.get("ticket_name"),
            "description": kw.get("description"),
            "category_id": kw.get("category_id"),
            "channel_id": request.env.ref("spp_grm.grm_ticket_channel_web").id,
            "partner_id": partner.id,
        }
        ticket = request.env["spp.grm.ticket"].sudo().create(vals)

        ticket.send_ticket_confirmation_email(ticket)

        return request.redirect("/my/tickets")
