# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AreaCustomSPPRole(models.Model):
    _inherit = "spp.area"

    @api.model
    def _prepare_domain(self, domain):
        domain = domain or []
        domain += [("id", "child_of", self.env.user.center_area_ids.ids)] if self.env.user.center_area_ids else []
        return domain

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        domain = self._prepare_domain(domain)
        return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = self._prepare_domain(domain)
        return super().search_read(domain, fields, offset, limit, order)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain = self._prepare_domain(domain)
        return super().web_search_read(domain, specification, offset, limit, order, count_limit)
