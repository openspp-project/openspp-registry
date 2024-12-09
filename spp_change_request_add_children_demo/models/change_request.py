import logging

from odoo import Command, api, models

_logger = logging.getLogger(__name__)


class ChangeRequestBaseCustomDemo(models.Model):
    _inherit = "spp.change.request"

    def create_request_detail_demo(self):
        """
        A version of spp.change.request create_request_detail function
        that does not check the applicant's phone number and
        does not load the CR details form
        :return:
        """
        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                # Set the dms directory
                _logger.debug("Change Request: DMS Directory Creation (%s)" % len(self.dms_directory_ids))
                # self.env.ref(self.env[res_model].DMS_STORAGE)
                dmsval = {
                    "is_root_directory": True,
                    "name": rec.name,
                }

                # Prepare CR type model data
                cr_type_vals = {
                    "registrant_id": rec.registrant_id.id,
                    "applicant_id": rec.applicant_id.id,
                    "change_request_id": rec.id,
                    "dms_directory_ids": [(Command.create(dmsval))],
                }

                # Create the change request detail record
                ref_id = self.env[res_model].create(cr_type_vals)
                directory_id = ref_id.dms_directory_ids[0].id

                self.env["spp.dms.directory"].create(
                    {
                        "name": "Applicant",
                        "parent_id": directory_id,
                        "is_root_directory": False,
                    }
                )

                # Upload Scanned IDs to DMS
                dms_file_ids = []
                for id_fld in ["id_document_details", "qr_code_details"]:
                    if rec[id_fld]:
                        dms_id_doc = rec._get_id_doc_vals(directory_id, id_fld)
                        if dms_id_doc:
                            dms_file_ids.append(Command.create(dms_id_doc))
                if dms_file_ids:
                    ref_id.update({"dms_file_ids": dms_file_ids})

                ref_id._onchange_registrant_id()
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                        "id_document_details": "",
                    }
                )

    # Temporary solution to phone number fo
    # def _check_phone_exist(self):
    #    pass

    @api.constrains("registrant_id", "applicant_phone")
    def _check_applicant_phone(self):
        # Temporary solution to phone number format error
        pass
