from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SPPFarmSeason(models.Model):
    _name = "spp.farm.season"
    _description = "Agricultural Season"
    _order = "date_start desc"

    name = fields.Char(
        string="Season Name",
        required=True,
        index=True,
    )
    description = fields.Text(
        string="Description",
    )
    date_start = fields.Date(
        string="Start Date",
        required=True,
        index=True,
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        index=True,
    )
    active = fields.Boolean(
        default=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        string="Status",
        default="draft",
        required=True,
        index=True,
    )
    activity_ids = fields.One2many(
        "spp.farm.activity",
        "season_id",
        string="Agricultural Activities",
    )
    activity_count = fields.Integer(
        string="Activities",
        compute="_compute_activity_count",
        store=True,
    )

    can_edit = fields.Boolean(
        string="Can Edit",
        compute="_compute_access_rights",
    )
    can_activate = fields.Boolean(
        string="Can Activate",
        compute="_compute_access_rights",
    )
    can_close = fields.Boolean(
        string="Can Close",
        compute="_compute_access_rights",
    )

    allow_overlap = fields.Boolean(
        string="Allow Overlap with Other Seasons",
        default=False,
        help="If checked, this season can overlap with other active seasons",
    )

    activity_type = fields.Selection(
        related="activity_ids.activity_type",
        store=False,
        readonly=True,
    )

    @api.depends("state")
    def _compute_access_rights(self):
        """Compute access rights based on user and state"""
        is_manager = self.env.user.has_group("spp_farmer_registry_base.group_spp_farm_manager")
        for record in self:
            record.can_edit = is_manager and record.state != "closed"
            record.can_activate = is_manager and record.state == "draft"
            record.can_close = is_manager and record.state == "active"

    @api.depends("activity_ids")
    def _compute_activity_count(self):
        for record in self:
            record.activity_count = len(record.activity_ids)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_end < record.date_start:
                raise ValidationError(_("End date must be after start date"))

    def action_activate(self):
        """Activate the season with proper security checks"""
        self.ensure_one()
        if not self.can_activate:
            raise ValidationError(_("You don't have permission to activate seasons"))
        if self.state != "draft":
            raise ValidationError(_("Only draft seasons can be activated"))
        self.write({"state": "active"})

    def action_close(self):
        """Close the season with proper security checks"""
        self.ensure_one()
        if not self.can_close:
            raise ValidationError(_("You don't have permission to close seasons"))
        if self.state != "active":
            raise ValidationError(_("Only active seasons can be closed"))
        self.write({"state": "closed"})

    def action_draft(self):
        """Reset season to draft state with proper security checks"""
        self.ensure_one()
        if not self.can_edit:
            raise ValidationError(_("You don't have permission to modify this season"))
        if self.state == "closed":
            raise ValidationError(_("Closed seasons cannot be reopened"))
        if self.activity_ids:
            raise ValidationError(_("Cannot reset to draft when activities exist"))
        self.write({"state": "draft"})

    @api.constrains("state")
    def _check_state_transition(self):
        """Validate state transitions"""
        for record in self:
            if record.state == "closed":
                # Check for ongoing activities
                ongoing = self.env["spp.farm.activity"].search_count([("season_id", "=", record.id)])
                if ongoing:
                    raise ValidationError(
                        _("Cannot close season with ongoing activities. " "Please complete or cancel them first.")
                    )

    @api.constrains("date_start", "date_end", "state")
    def _check_overlapping_active_seasons(self):
        """Prevent overlapping active seasons unless explicitly allowed"""
        for record in self:
            if record.state == "active":
                overlapping = self.search(
                    [
                        ("id", "!=", record.id),
                        ("state", "=", "active"),
                        "|",
                        "&",
                        ("date_start", "<=", record.date_start),
                        ("date_end", ">=", record.date_start),
                        "&",
                        ("date_start", "<=", record.date_end),
                        ("date_end", ">=", record.date_end),
                    ]
                )
                if overlapping and not self.allow_overlap:
                    raise ValidationError(
                        _(
                            "This season overlaps with existing active seasons: %s. "
                            "If this is intended, please use the 'Allow Overlap' option."
                        )
                        % ", ".join(overlapping.mapped("name"))
                    )

    def toggle_active(self):
        """Override to prevent archiving closed seasons with activities"""
        for record in self:
            if not record.active and record.state == "closed":
                if record.activity_ids:
                    raise ValidationError(_("Cannot reactivate closed season with existing activities"))
        return super().toggle_active()

    @api.model
    def _get_current_season(self):
        """Helper method to get current active season"""
        today = fields.Date.today()
        current_season = self.search(
            [
                ("state", "=", "active"),
                ("date_start", "<=", today),
                ("date_end", ">=", today),
            ],
            limit=1,
            order="date_start desc",
        )
        return current_season

    def copy(self, default=None):
        """Override copy to handle unique constraints and naming"""
        self.ensure_one()
        default = dict(default or {})

        # Handle name uniqueness
        if "name" not in default:
            default["name"] = _("%s (Copy)") % self.name

        # Reset state and dates
        default.update(
            {
                "state": "draft",
                "activity_ids": [],
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today(),
            }
        )

        return super().copy(default)

    def write(self, vals):
        """Override write to implement state-based access control"""
        for record in self:
            if not record.can_edit and (set(vals.keys()) - {"message_ids", "message_follower_ids"}):
                raise ValidationError(_("You don't have permission to modify this season"))
        return super().write(vals)

    @api.model
    def create(self, vals):
        """Override create to implement creation access control"""
        if not self.env.user.has_group("spp_farmer_registry_base.group_spp_farm_manager"):
            raise ValidationError(_("Only managers can create seasons"))
        return super().create(vals)

    def unlink(self):
        """Override unlink to implement deletion access control"""
        for record in self:
            if not record.can_edit:
                raise ValidationError(_("You don't have permission to delete this season"))
            if record.state == "closed":
                raise ValidationError(_("Closed seasons cannot be deleted"))
        return super().unlink()

    def _compute_display_name(self):
        """Modern approach to custom display names"""
        for record in self:
            record.display_name = f"{record.name} ({record.date_start} to {record.date_end})"

    def name_get(self):
        """Custom name display including dates"""
        result = []
        for record in self:
            name = f"{record.name} ({record.date_start.strftime('%Y-%m-%d')} to {record.date_end.strftime('%Y-%m-%d')})"
            result.append((record.id, name))
        return result

    def action_view_activities(self):
        """Open the activities related to this season"""
        self.ensure_one()
        action = {
            "name": _("Season Activities"),
            "type": "ir.actions.act_window",
            "res_model": "spp.farm.activity",
            "view_mode": "tree,form",
            "domain": [("season_id", "=", self.id)],
            "context": {"default_season_id": self.id},
        }
        return action

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Season name must be unique!"),
        ("date_check", "CHECK(date_end >= date_start)", "End date must be after start date"),
    ]
