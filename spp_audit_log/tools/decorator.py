# (C) 2021 Smile (<https://www.smile.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import copy
import logging

from odoo import api

long = int

_logger = logging.getLogger(__name__)


def get_new_values(records):
    new_values = []
    for record in records:
        vals = {}
        for fname in records._fields:
            try:
                vals[fname] = records._fields[fname].convert_to_read(record[fname], record, use_display_name=False)
            except TypeError as e:
                _logger.warning("Error converting field %s: %s", fname, e)
        new_values.append(vals)
    return new_values


def audit_decorator(method):
    """
    The audit_decorator function is a Python decorator that adds auditing functionality to create, write, and
    unlink methods of a class.

    :param method: The `method` parameter is a string that specifies the type of operation being
    performed. It can have one of the following values: "create", "write", or "unlink"
    :return: The audit_decorator function returns one of three functions: audit_create, audit_write, or
    audit_unlink, depending on the value of the method parameter.
    """

    @api.model
    def audit_create(self, vals):
        result = audit_create.origin(self, vals)
        record = self.browse(result) if isinstance(result, int | long) else result
        rules = self.get_audit_rules("create")

        new_values = record.read(load="_classic_write")
        if new_values:
            keys = new_values[0].keys()
            for key in keys:
                if str(type(new_values[0][key])) == "<class 'markupsafe.Markup'>":
                    new_values[0][key] = str(new_values[0][key])

            rules.log("create", new_values=new_values)
        return result

    def audit_write(self, vals):
        rules = self.get_audit_rules("write")
        old_values_copy = None
        if rules:
            old_values = self.sudo().with_context(allowed_company_ids=[]).read(load="_classic_write")
            old_values_copy = copy.deepcopy(old_values)
        result = audit_write.origin(self, vals)

        if audit_write.origin.__name__ == "_write":
            new_values = get_new_values(self)
        else:
            new_values = self.sudo().with_context(allowed_company_ids=[]).read(load="_classic_write")

        if new_values and old_values_copy:
            keys = new_values[0].keys()
            for key in keys:
                if str(type(new_values[0][key])) == "<class 'markupsafe.Markup'>":
                    new_values[0][key] = str(new_values[0][key])
                    old_values_copy[0][key] = str(old_values_copy[0][key])

            if audit_write.origin.__name__ == "write":
                rules.log("write", old_values_copy, new_values)
        return result

    def audit_unlink(self):
        rules = self.get_audit_rules("unlink")
        old_values = self.read(load="_classic_write")

        if old_values:
            keys = old_values[0].keys()
            for key in keys:
                if str(type(old_values[0][key])) == "<class 'markupsafe.Markup'>":
                    old_values[0][key] = str(old_values[0][key])

            rules.log("unlink", old_values)
        return audit_unlink.origin(self)

    methods = {
        "create": audit_create,
        "write": audit_write,
        "_write": audit_write,
        "unlink": audit_unlink,
    }

    return methods[method]
