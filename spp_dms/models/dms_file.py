import base64
import hashlib
import json
import logging
from collections import defaultdict

from PIL import Image

from odoo import api, fields, models, tools
from odoo.tools import human_size
from odoo.tools.mimetypes import guess_mimetype

from ..tools import file_tools

_logger = logging.getLogger(__name__)


class SPPDMSFile(models.Model):
    _name = "spp.dms.file"
    _inherit = [
        "spp.dms.mixins.thumbnail",
    ]
    _description = "DMS File"
    _order = "name asc"

    name = fields.Char(required=True, index="btree", string="Filename")
    directory_id = fields.Many2one(
        comodel_name="spp.dms.directory",
        string="Directory",
        ondelete="restrict",
        auto_join=True,
        required=True,
        index="btree",
    )
    path_names = fields.Char(
        compute="_compute_path",
        compute_sudo=True,
        readonly=True,
        store=False,
    )
    path_json = fields.Text(
        compute="_compute_path",
        compute_sudo=True,
        readonly=True,
        store=False,
    )
    content = fields.Binary(
        compute="_compute_content",
        inverse="_inverse_content",
        attachment=False,
        prefetch=False,
        required=True,
        store=False,
    )
    extension = fields.Char(compute="_compute_extension", readonly=True, store=True)
    mimetype = fields.Char(compute="_compute_mimetype", string="Type", readonly=True, store=True)

    size = fields.Float(readonly=True)
    human_size = fields.Char(readonly=True, compute="_compute_human_size", store=True)
    checksum = fields.Char(string="Checksum/SHA512", readonly=True, index="btree")
    content_file = fields.Binary(attachment=True, prefetch=False)

    category_id = fields.Many2one(
        comodel_name="spp.dms.category",
        string="Category",
        ondelete="restrict",
        auto_join=True,
        index="btree",
    )

    image_1920 = fields.Image(compute="_compute_image_1920", store=True, readonly=False)
    color = fields.Integer(default=0)

    @api.depends("mimetype", "content")
    def _compute_image_1920(self):
        """Provide thumbnail automatically if possible."""
        for one in self.filtered("mimetype"):
            # Image.MIME provides a dict of mimetypes supported by Pillow,
            # SVG is not present in the dict but is also a supported image format
            # lacking a better solution, it's being added manually
            # Some component modifies the PIL dictionary by adding PDF as a valid
            # image type, so it must be explicitly excluded.
            if one.mimetype != "application/pdf" and one.mimetype in (
                *Image.MIME.values(),
                "image/svg+xml",
            ):
                one.image_1920 = one.content

    @api.depends("name", "directory_id", "directory_id.parent_path")
    def _compute_path(self):
        model = self.env["spp.dms.directory"]
        for record in self:
            if record.display_name:
                path_names = [record.display_name]
                path_json = [
                    {
                        "model": record._name,
                        "name": record.display_name,
                        "id": isinstance(record.id, int) and record.id or 0,
                    }
                ]
                current_dir = record.directory_id
                while current_dir:
                    path_names.insert(0, current_dir.name)
                    path_json.insert(
                        0,
                        {
                            "model": model._name,
                            "name": current_dir.name,
                            "id": current_dir._origin.id,
                        },
                    )
                    current_dir = current_dir.parent_id
                record.update(
                    {
                        "path_names": "/".join(path_names),
                        "path_json": json.dumps(path_json),
                    }
                )
            else:
                record.update(
                    {
                        "path_names": "/",
                        "path_json": None,
                    }
                )

    @api.depends("content_file")
    def _compute_content(self):
        bin_size = self.env.context.get("bin_size", False)
        for record in self:
            if record.content_file:
                context = {"human_size": True} if bin_size else {"base64": True}
                record.content = record.with_context(**context).content_file

    def _inverse_content(self):
        updates = defaultdict(set)
        for record in self:
            values = {"content_file": False}
            binary = base64.b64decode(record.content or "")
            values = record._update_content_vals(values, binary)
            updates[tools.frozendict(values)].add(record.id)
        # with self.env.norecompute():
        for vals, ids in updates.items():
            self.browse(ids).write(dict(vals))

    def _update_content_vals(self, vals, binary):
        new_vals = vals.copy()
        new_vals.update(
            {
                "checksum": self._get_checksum(binary),
                "size": binary and len(binary) or 0,
            }
        )
        new_vals["content_file"] = self.content
        return new_vals

    def _get_checksum(self, binary):
        return hashlib.sha512(binary or b"").hexdigest()

    @api.depends("name", "mimetype", "content")
    def _compute_extension(self):
        for record in self:
            record.extension = file_tools.guess_extension(record.name, record.mimetype, record.content)

    @api.depends("content")
    def _compute_mimetype(self):
        for record in self:
            try:
                binary = base64.b64decode(record.content or "")
            except Exception:
                _logger.info("DEBUG: _compute_mimetype: %s" % record.content)
            else:
                record.mimetype = guess_mimetype(binary)

    @api.depends("size")
    def _compute_human_size(self):
        for item in self:
            item.human_size = human_size(item.size)
