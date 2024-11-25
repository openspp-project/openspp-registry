# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class G2PAssignToProgramWizard(models.TransientModel):
    _name = "g2p.assign.program.wizard"
    _description = "Add Registrants to Program Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            # Get the first selected registrant and check if group or individual
            partner_id = self.env.context.get("active_ids")[0]
            registrant = self.env["res.partner"].search(
                [
                    ("id", "=", partner_id),
                ]
            )
            target_type = "group" if registrant.is_group else "individual"
            res["target_type"] = target_type
            return res
        else:
            raise UserError(_("There are no selected registrants!"))

    target_type = fields.Selection(selection=[("group", "Group"), ("individual", "Individual")])
    program_id = fields.Many2one(
        "g2p.program",
        "",
        domain="[('target_type', '=', target_type), ('state', '=', 'active')]",
        help="A program",
        required=True,
    )

    # ruff: noqa: C901
    def assign_registrant(self):
        if self.env.context.get("active_ids"):
            partner_ids = self.env.context.get("active_ids")
            _logger.debug("Adding to Program Wizard with registrant record IDs: %s" % partner_ids)
            ctr = 0
            ig_ctr = 0
            ok_ctr = 0
            message = None
            kind = "success"
            for rec in self.env["res.partner"].search([("id", "in", partner_ids)]):
                if self.program_id not in rec.program_membership_ids.program_id:
                    ctr += 1
                    _logger.debug(f"Processing ({ctr}): {rec.name}")
                    proceed = False
                    # Do not include disabled registrants
                    if rec.disabled:
                        ctr -= 1
                        # ig_ctr += 1
                        _logger.debug("Ignored because registrant is disabled: %s" % rec.name)
                    else:
                        if rec.is_group:  # Get only group registrants
                            if self.target_type == "group":
                                proceed = True
                            else:
                                ig_ctr += 1
                                _logger.debug("Ignored because registrant is not a group: %s" % rec.name)
                        else:  # Get only individual registrants
                            if self.target_type == "individual":
                                proceed = True
                            else:
                                ig_ctr += 1
                                _logger.debug(
                                    "Ignored because registrant is not an individual: %s" % rec.name
                                )
                    if proceed:
                        ok_ctr += 1
                        vals = {
                            "partner_id": rec.id,
                            "program_id": self.program_id.id,
                        }
                        _logger.debug("Adding to Program Membership: %s" % vals)
                        self.env["g2p.program_membership"].create(vals)
                else:
                    ig_ctr += 1
                    _logger.debug(
                        f"{rec.name} was ignored because the registrant is already in the Program"
                        f"{self.program_id.name}"
                    )
            _logger.debug(
                f"Total selected registrants:{ctr}, Total ignored:{ig_ctr}, Total added to group:{ok_ctr}"
            )

            if len(partner_ids) == 1:
                if rec.disabled and rec.is_group:
                    message = _("Disabled group can't be added to the program.") % {
                        "registrant": rec.name,
                        "program": self.program_id.name,
                    }
                    kind = "danger"
                elif rec.disabled and not rec.is_group:
                    message = _("Disabled individaul can't be added to the program.") % {
                        "registrant": rec.name,
                        "program": self.program_id.name,
                    }
                    kind = "danger"

                elif ig_ctr and not rec.disabled:
                    message = _("%(registrant)s was already in the Program %(program)s") % {
                        "registrant": rec.name,
                        "program": self.program_id.name,
                    }
                    kind = "danger"
                else:
                    message = _("%(registrant)s is added to the Program %(program)s") % {
                        "registrant": rec.name,
                        "program": self.program_id.name,
                    }
                    kind = "warning"

            else:
                if not ctr and not rec.disabled:
                    message = _("Registrant's was already in the Program %s") % self.program_id.name
                    kind = "danger"
                elif not ctr and rec.disabled and rec.is_group:
                    message = _("Disabled group(s) can't be added to the program %s") % self.program_id.name
                    kind = "danger"
                elif not ctr and rec.disabled and not rec.is_group:
                    message = (
                        _("Disabled Individual(s) can't be added to the program %s") % self.program_id.name
                    )
                    kind = "danger"
                else:
                    message = _(
                        "Total registrants:%(total)s, Already in program:%(existing)s, Newly added:%(new)s"
                    ) % {"total": ctr + ig_ctr, "existing": ig_ctr, "new": ok_ctr}
                    kind = "warning"

            if message:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

    def open_wizard(self):
        # _logger.debug("Registrant IDs: %s" % self.env.context.get("active_ids"))
        return {
            "name": "Add to Program",
            "view_mode": "form",
            "res_model": "g2p.assign.program.wizard",
            "view_id": self.env.ref("g2p_programs.assign_to_program_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }


class G2PAssignToProgramRegistrants(models.TransientModel):
    _name = "g2p.assign.program.registrants"
    _description = "Registrant Assign to Program"

    state = fields.Selection(
        [
            ("New", "New"),
            ("Okay", "Okay"),
            ("Conflict", "Conflict"),
            ("Assigned", "Assigned"),
        ],
        "Status",
        readonly=True,
        default="New",
    )
