# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import logging
import math
from io import BytesIO

from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)
_area_import_raw_model = "spp.area.import.raw"
_res_lang_model = "res.lang"
_area_import_channel = "root.area_import"


class OpenSPPAreaImport(models.Model):
    _name = "spp.area.import"
    _description = "Areas Import Table"
    _users_model = "res.users"

    MIN_ROW_JOB_QUEUE = 400

    NEW = "New"
    UPLOADED = "Uploaded"
    IMPORTED = "Imported"
    VALIDATED = "Validated"
    DONE = "Done"
    CANCELLED = "Cancelled"

    STATE_SELECTION = [
        (NEW, NEW),
        (UPLOADED, UPLOADED),
        (IMPORTED, IMPORTED),
        (VALIDATED, VALIDATED),
        (DONE, DONE),
        (CANCELLED, CANCELLED),
    ]

    name = fields.Char("File Name", required=True, translate=True)
    excel_file = fields.Binary("Area Excel File")
    date_uploaded = fields.Datetime()

    upload_id = fields.Many2one(_users_model, "Uploaded by")
    date_imported = fields.Datetime()
    import_id = fields.Many2one(_users_model, "Imported by")
    date_validated = fields.Datetime()
    validate_id = fields.Many2one(_users_model, "Validated by")
    raw_data_ids = fields.One2many(_area_import_raw_model, "area_import_id", "Raw Data")
    tot_rows_imported = fields.Integer(
        "Total Rows Imported",
        compute="_compute_get_total_rows",
        store=True,
        readonly=True,
    )
    tot_rows_error = fields.Integer(
        "Total Rows with Error",
        compute="_compute_get_total_rows",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        STATE_SELECTION,
        "Status",
        default=NEW,
    )

    locked = fields.Boolean(default=False)
    locked_reason = fields.Char(readonly=True)

    @api.onchange("excel_file")
    def excel_file_change(self):
        """
        The above function is an onchange function in Python that updates the date_uploaded, upload_id,
        and state fields based on the value of the excel_file field.
        """

        if self.name:
            self.update(
                {
                    "date_uploaded": fields.Datetime.now(),
                    "upload_id": self.env.user,
                    "state": self.UPLOADED,
                }
            )
        else:
            self.update({"date_uploaded": None, "upload_id": None, "state": self.UPLOADED})

    @api.depends("raw_data_ids", "raw_data_ids.state")
    def _compute_get_total_rows(self):
        """
        The function `_compute_get_total_rows` calculates the total number of imported rows and the
        total number of rows with an error for a given record.
        """
        for rec in self:
            tot_rows_imported = len(rec.raw_data_ids)
            tot_rows_error = self.env[_area_import_raw_model].search(
                [("id", "in", rec.raw_data_ids.ids), ("state", "=", "Error")]
            )
            rec.update(
                {
                    "tot_rows_imported": tot_rows_imported,
                    "tot_rows_error": len(tot_rows_error),
                }
            )

    def cancel_import(self):
        """
        The function cancels the import by updating the state of the record to "Cancelled".
        """
        for rec in self:
            rec.update({"state": self.CANCELLED})

    def reset_to_uploaded(self):
        """
        The function resets the state of a record to "Uploaded".
        """
        for rec in self:
            rec.update({"state": self.UPLOADED})

    def get_column_indexes(self, columns, area_level):
        self.ensure_one()
        default_lang = self.env.context.get("lang", "en_US")
        if default_lang not in columns:
            default_lang = "en_US"
        default_iso_code = default_lang.split("_")[0].upper()

        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        if not active_languages:
            raise ValidationError(_("No active language found."))

        # Get column prefix and the language iso code used in the name header
        lang_codes = active_languages.read(fields=["code", "iso_code"])
        column_name_prefix = f"ADM{area_level}"

        # Get Column name to be used as name field in the area
        name_headers = {code["code"]: f"{column_name_prefix}_{code['iso_code'].upper()}" for code in lang_codes}

        # Get Column name to be used as code field in the area
        code_header = f"{column_name_prefix}_PCODE"

        # get name and code column indexes
        name_indexes = {}
        for name_header in name_headers:
            try:
                name_indexes.update({name_header: columns.index(name_headers[name_header])})
            except ValueError as e:
                _logger.warning("Column header not found: %s", e)
        code_index = columns.index(code_header)

        # Get index of the Parent header of the area if area level is not 0
        parent_name_index = None
        parent_code_index = None
        if area_level != 0:
            parent_name_header = f"{column_name_prefix[:3]}{area_level - 1}_{default_iso_code}"
            parent_code_header = f"{column_name_prefix[:3]}{area_level - 1}_PCODE"

            parent_name_index = columns.index(parent_name_header)
            parent_code_index = columns.index(parent_code_header)

        # Get area_sqkm column index
        area_sqkm_index = None
        if "AREA_SQKM" in columns:
            area_sqkm_index = columns.index("AREA_SQKM")

        return {
            "name_indexes": name_indexes,
            "code_index": code_index,
            "parent_name_index": parent_name_index,
            "parent_code_index": parent_code_index,
            "area_sqkm_index": area_sqkm_index,
        }

    def get_area_vals(self, column_indexes, row, sheet, area_level):
        self.ensure_one()
        default_lang = self.env.context.get("lang", "en_US")
        if default_lang not in column_indexes["name_indexes"]:
            default_lang = "en_US"
        vals = {
            "admin_name": sheet.cell(row, column_indexes["name_indexes"][default_lang]).value,
            "admin_code": sheet.cell(row, column_indexes["code_index"]).value,
            "parent_name": "",
            "parent_code": "",
            "level": area_level,
            "area_import_id": self.id,
        }
        if column_indexes["area_sqkm_index"]:
            vals["area_sqkm"] = sheet.cell(row, column_indexes["area_sqkm_index"]).value

        if column_indexes["parent_name_index"] is not None and column_indexes["parent_code_index"] is not None:
            vals["parent_name"] = sheet.cell(row, column_indexes["parent_name_index"]).value
            vals["parent_code"] = sheet.cell(row, column_indexes["parent_code_index"]).value

        return vals

    def create_import_raw(self, vals, column_indexes, row, sheet):
        self.ensure_one()
        import_raw_id = self.env[_area_import_raw_model].create(vals)
        for lang_code in column_indexes["name_indexes"]:
            lang_name = sheet.cell(row, column_indexes["name_indexes"][lang_code]).value
            import_raw_id.with_context(lang=lang_code).write(
                {
                    "admin_name": lang_name,
                }
            )

    def _get_book(self):
        self.ensure_one()
        try:
            inputx = BytesIO()
            inputx.write(base64.decodebytes(self.excel_file))
        except TypeError as e:
            raise ValidationError(_("ERROR: {}").format(e)) from e
        return open_workbook(file_contents=inputx.getvalue())

    def check_all_languages_activated(self, columns, area_level):
        """Check if all languages in the specified columns are activated.

        Args:
            columns (list): The list of column names to check.
            area_level (int): The administrative area level to check within the column names.

        Raises:
            ValidationError: If any language is not active.
        """
        self.ensure_one()
        prefix = f"ADM{area_level}_"
        active_langs = self.env[_res_lang_model].search([("active", "=", True)]).mapped("iso_code")

        for col in columns:
            if col.startswith(prefix):
                lang = col.split("_", 1)[1]
                if len(lang) == 2 and lang.lower() not in active_langs:
                    raise ValidationError(
                        _(
                            "Language with ISO Code %s is not active.\n"
                            "Please request the administrator to enable the desired language."
                        )
                        % lang.upper()
                    )

    def import_data(self):
        self.ensure_one()

        _logger.info("Area Import: Started: %s" % fields.Datetime.now())
        # Delete all existing import data for this record
        # This can only be happen if the Area Upload record is reset back to Uploaded state
        if self.raw_data_ids:
            self.raw_data_ids.unlink()

        _logger.info("Area Import: Loading Excel File: %s" % fields.Datetime.now())
        # Wrap binary to BytesIO

        book = self._get_book()

        sheet_names = book.sheet_names()
        sheet_names.sort()
        self.locked = True
        self.locked_reason = _("Importing data.")

        jobs = []

        for area_level, sheet_name in enumerate(sheet_names):
            sheet = book.sheet_by_name(sheet_name)
            columns = sheet.row_values(0)
            self.check_all_languages_activated(columns, area_level)
            column_indexes = self.get_column_indexes(columns, area_level)

            batches = math.ceil(sheet.nrows / 1000)
            for i in range(batches):
                if i == 0:
                    start = 1
                else:
                    start = i * 1000
                end = min((i + 1) * 1000, sheet.nrows)
                jobs.append(
                    self.delayable(channel=_area_import_channel)._import_data(
                        sheet_name, column_indexes, start, end, area_level
                    )
                )

        main_job = group(*jobs)

        main_job.on_done(self.delayable(channel=_area_import_channel)._async_mark_done())
        main_job.delay()

    def _import_data(self, sheet_name, column_indexes, start, end, area_level):
        """
        The `import_data` function imports data from an Excel file, processes it, and updates the record
        with the imported data.
        """
        self.ensure_one()

        book = self._get_book()

        sheet = book.sheet_by_name(sheet_name)
        for row in range(start, end):
            import_raw_vals = self.get_area_vals(column_indexes, row, sheet, area_level)
            self.create_import_raw(import_raw_vals, column_indexes, row, sheet)

        self.update(
            {
                "date_imported": fields.Datetime.now(),
                "import_id": self.env.user,
                "date_validated": fields.Datetime.now(),
                "validate_id": self.env.user,
                "state": self.IMPORTED,
            }
        )

    def validate_raw_data(self):
        """
        The function iterates through a collection of records and checks if the count of raw data is
        less than a minimum threshold, and if so, it calls a validation function, otherwise it calls an
        """
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Validating data.")
            batches = math.ceil(len(rec.raw_data_ids) / 1000)
            jobs = []
            for i in range(batches):
                start = i * 1000
                end = min((i + 1) * 1000, len(rec.raw_data_ids))
                jobs.append(rec.delayable(channel=_area_import_channel)._validate_raw_data(rec.raw_data_ids[start:end]))
            main_job = group(*jobs)
            main_job.on_done(rec.delayable(channel=_area_import_channel)._validate_mark_done())
            main_job.delay()

    def _validate_raw_data(self, raw_data_ids):
        """
        The function validates raw data and updates the state if there are no errors.
        """
        self.ensure_one()
        raw_data_ids.validate_raw_data()

    def _validate_mark_done(self):
        self.locked = False
        self.locked_reason = None
        self.ensure_one()
        if not self.env[_area_import_raw_model].search([("id", "in", self.raw_data_ids.ids), ("state", "=", "Error")]):
            self.update(
                {
                    "state": self.VALIDATED,
                }
            )

    def fix_area_level_and_kind(self):
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Fixing area level.")
            batches = math.ceil(len(rec.raw_data_ids) / 1000)
            jobs = []
            for i in range(batches):
                start = i * 1000
                end = min((i + 1) * 1000, len(rec.raw_data_ids))
                jobs.append(
                    rec.delayable(channel=_area_import_channel)._fix_area_level_and_kind(rec.raw_data_ids[start:end])
                )
            main_job = group(*jobs)
            main_job.on_done(rec.delayable(channel=_area_import_channel)._async_mark_done())
            main_job.delay()

    def _fix_area_level_and_kind(self, raw_data_ids):
        """
        The function `fix_area_level_and_kind` fixes the area level of the raw data.
        """
        self.ensure_one()
        raw_data_ids.fix_area_level_and_kind()

    def _async_mark_done(self, function_mark_done=None):
        """
        The function `_async_mark_done` unlocks a resource by setting the `locked` attribute to `False`
        and clearing the `locked_reason` attribute.
        """
        self.ensure_one()

        self.locked = False
        self.locked_reason = None

        if function_mark_done:
            getattr(self, function_mark_done)()

    def save_to_area(self):
        """
        The function saves data to an area, either synchronously or asynchronously depending on the
        number of raw data records.
        """
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Importing data.")
            rec._async_recursive_save_to_area(rec.raw_data_ids)

    def _async_recursive_save_to_area(self, raw_data_ids):
        """
        This is to ensure that the function `_save_to_area` is called recursively and in order until all raw data
        is saved to the area.
        """
        self.ensure_one()
        jobs = []
        jobs.append(self.delayable(channel=_area_import_channel)._save_to_area(raw_data_ids[:1000]))
        main_job = group(*jobs)
        count = len(raw_data_ids)
        if count <= 1000:
            main_job.on_done(self.delayable(channel=_area_import_channel)._save_to_area_mark_done())
        else:
            main_job.on_done(
                self.delayable(channel=_area_import_channel)._async_recursive_save_to_area(raw_data_ids[1000:])
            )
        main_job.delay()

    def _save_to_area(self, raw_data_ids):
        """
        The function saves raw data to an area and updates the state to "DONE".
        """
        self.ensure_one()

        raw_data_ids.save_to_area()

    def _save_to_area_mark_done(self):
        self.ensure_one()
        self.locked = False
        self.locked_reason = None
        if not self.env[_area_import_raw_model].search(
            [("id", "in", self.raw_data_ids.ids), ("state", "=", "Validated")]
        ):
            self.update(
                {
                    "state": self.DONE,
                }
            )

    def refresh_page(self):
        """
        The function `refresh_page` returns a dictionary with the type and tag values to reload the
        page.
        :return: The code is returning a dictionary with two key-value pairs. The "type" key has the
        value "ir.actions.client" and the "tag" key has the value "reload".
        """
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }


# Assets Import Raw Data
class OpenSPPAreaImportActivities(models.Model):
    _name = _area_import_raw_model
    _description = "Area Import Raw Data"
    _order = "level"
    _area_model = "spp.area"

    NEW = "New"
    VALIDATED = "Validated"
    ERROR = "Error"
    UPDATED = "Updated"
    POSTED = "Posted"

    STATE_CHOICES = [
        (NEW, NEW),
        (VALIDATED, VALIDATED),
        (ERROR, ERROR),
        (UPDATED, UPDATED),
        (POSTED, POSTED),
    ]

    STATE_ORDER_STATE = {
        ERROR: 0,
        NEW: 1,
        VALIDATED: 2,
        UPDATED: 3,
        POSTED: 4,
    }

    area_import_id = fields.Many2one("spp.area.import", "Area Import", required=True)
    admin_name = fields.Char(translate=True)
    admin_code = fields.Char()

    parent_name = fields.Char()
    parent_code = fields.Char()

    level = fields.Integer()

    area_sqkm = fields.Char("Area (sq/km)")

    remarks = fields.Text("Remarks/Errors")
    state = fields.Selection(
        STATE_CHOICES,
        "Status",
        default="New",
    )
    state_order = fields.Integer(
        compute="_compute_state_order",
        store=True,
    )
    area_id = fields.Many2one(_area_model, "Area", readonly=True)

    @api.depends("state")
    def _compute_state_order(self):
        for rec in self:
            rec.state_order = self.STATE_ORDER_STATE[rec.state]

    def check_errors(self):
        self.ensure_one()
        errors = []
        if not self.admin_name or not self.admin_code:
            errors.append(_("Name and Code of area is required."))

        if self.area_sqkm:
            try:
                float(self.area_sqkm)
            except ValueError:
                errors.append(_("AREA_SQKM should be numerical."))

        if self.level == 0 and (self.parent_name or self.parent_code):
            errors.append(_("Level 0 area should not have a parent name and parent code."))

        if self.level != 0 and (not self.parent_name or not self.parent_code):
            errors.append(_("Level 1 and above area should have a parent name and parent code."))
        return errors

    def validate_raw_data(self):
        for rec in self:
            errors = rec.check_errors()

            if errors:
                state = self.ERROR
                remarks = "\n".join(errors)
            else:
                state = self.VALIDATED
                remarks = "No Error"

            rec.write(
                {
                    "remarks": remarks,
                    "state": state,
                }
            )

    def get_area_vals(self):
        self.ensure_one()

        parent_id = None
        if self.parent_name and self.parent_code:
            parent_id = (
                self.env[self._area_model]
                .search(
                    [
                        ("code", "=", self.parent_code),
                    ],
                    limit=1,
                )
                .id
            )

        area_sqkm = self.area_sqkm

        try:
            area_sqkm = float(area_sqkm)
        except ValueError:
            area_sqkm = 0.0

        return {
            "parent_id": parent_id,
            "draft_name": self.admin_name,
            "code": self.admin_code,
            "area_sqkm": area_sqkm,
            "kind": self.env.ref("spp_area_base.admin_area_kind").id,
        }

    def save_to_area(self):
        """
        The function saves data to the "spp.area" model in the database, updating existing records if
        they exist and creating new records if they don't.
        """
        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        for rec in self:
            area_vals = rec.get_area_vals()
            if area_id := self.env[self._area_model].search([("code", "=", rec.admin_code)]):
                state = self.UPDATED
                area_id.update(area_vals)
            else:
                state = self.POSTED
                area_id = self.env[self._area_model].create(area_vals)

            for lang in active_languages:
                area_id.with_context(lang=lang.code).write(
                    {
                        "draft_name": rec.with_context(lang=lang.code).admin_name,
                    }
                )
                area_id.with_context(lang=lang.code)._compute_name()
                area_id.with_context(lang=lang.code)._compute_complete_name()

            rec.update(
                {
                    "state": state,
                    "remarks": "Successfully save to Area",
                    "area_id": area_id.id,
                }
            )

    def fix_area_level_and_kind(self):
        for rec in self:
            if rec.area_id and (rec.area_id.area_level != rec.level or not rec.area_id.kind):
                parent_id = None
                if rec.parent_name and rec.parent_code:
                    parent_id = (
                        self.env[self._area_model]
                        .search(
                            [
                                ("code", "=", rec.parent_code),
                            ],
                            limit=1,
                        )
                        .id
                    )
                rec.area_id.update(
                    {
                        "kind": rec.env.ref("spp_area_base.admin_area_kind").id,
                        "parent_id": parent_id,
                    }
                )
