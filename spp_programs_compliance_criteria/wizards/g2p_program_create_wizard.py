import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2pProgramCreateWizard(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    compliance_criteria = fields.Boolean()
    compliance_kind = fields.Selection(
        selection=[
            ("g2p.program_membership.manager.default", "Default"),
        ],
        default="g2p.program_membership.manager.default",
    )
    compliance_domain = fields.Text(default="[]")

    def create_program(self):
        action = super().create_program()
        if self.compliance_criteria:
            program = self.env["g2p.program"].browse(action["res_id"])
            self._create_compliance_manager(program)
        return action

    def _check_compliance_manager_info(self):
        self.ensure_one()
        if not self.compliance_criteria:
            return
        err_msg = _("Not enough information for creating compliance manager!")
        if not self.compliance_kind:
            raise ValidationError(err_msg)
        if self.compliance_kind == "g2p.program_membership.manager.default" and not self.compliance_domain:
            raise ValidationError(err_msg)

    def _create_compliance_manager(self, program):
        self.ensure_one()
        program.ensure_one()
        self._check_compliance_manager_info()
        manager = self.env[self.compliance_kind].sudo().create(self._prepare_compliance_criteria_create_vals(program))
        program.write(
            {
                "compliance_managers": [
                    (
                        0,
                        0,
                        {
                            "manager_ref_id": "%s,%d" % (self.compliance_kind, manager.id),
                        },
                    ),
                ],
            }
        )

    def _prepare_compliance_criteria_create_vals(self, program):
        """
        Preparing vals for creating compliance criteria manager for new program.

        :param program: instance of g2p.program()
        :return (dictionary): create vals for compliance criteria manager
        :raise: NotImplementedError for compliance_kind not yet existed

        How to inherit this function:
        ```python
            def _prepare_compliance_criteria_create_vals(self, program):
                if self.compliance_kind = "new.manager.type":
                    return {
                        "key": "value",
                        ...
                    }
                return super()._prepare_compliance_criteria_create_vals(program)
        ```
        """
        if self.compliance_kind == "g2p.program_membership.manager.default":
            return {
                "name": "Default",
                "program_id": program.id,
                "admin_area_ids": [(6, 0, self.admin_area_ids.ids)],
                "eligibility_domain": self.compliance_domain,
            }
        raise NotImplementedError()
