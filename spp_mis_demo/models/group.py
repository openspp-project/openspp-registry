# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

CHILDREN_AGE_LIMIT = 18
ELDERLY_AGE_LIMIT = 65


class G2PGroup(models.Model):
    _inherit = "res.partner"

    """
    Source:
    OK ➢ Households (HH) with children - extracted from demographic data of HH adult members plus child members
    OK ➢ Households (HH) with children aged 12-18 - extracted from demographic data of HH adult members
    plus childmembers
    OK ➢ Households (HH) with children aged 0-11 - extracted from demographic data of HH adult members
    plus child members
    OK ➢ single-headed HH - extracted from demographic data of HH adult members
    OK ➢ female-headed HH - extracted from demographic data of HH adult members
    OK ➢ HH with pregnant/lactating women - extracted from vulnerability indicator
    OK ➢ HH with elderly (including single / elderly-headed HHs) - extracted from demographic
    data of HH adult members
    OK ➢ HHs with disabled (mental or physical) members - extracted from vulnerability indicator
    OK ➢ HHs with members that have chronic illness/medical conditions - extracted from
    vulnerability indicator
"""
    z_ind_grp_num_children = fields.Integer(
        "Number of children",
        compute="_compute_ind_grp_num_children",
        help="Households (HH) with children - extracted from demographic data of "
        "HH adult members plus child members",
        store=True,
    )
    z_ind_grp_num_children_12_and_above = fields.Integer(
        "Number of children aged 12 and above",
        compute="_compute_ind_grp_num_children_12_and_above",
        help="Households (HH) with children - extracted from demographic data of "
        "HH adult members plus child members",
        store=True,
    )
    z_ind_grp_num_children_11_and_below = fields.Integer(
        "Number of children aged 11 and below",
        compute="_compute_ind_grp_num_children_11_and_below",
        help="Households (HH) with children - extracted from demographic data of "
        "HH adult members plus child members",
        store=True,
    )
    z_ind_grp_num_members = fields.Integer("Number of members", compute="_compute_ind_grp_num_members", store=True)
    z_ind_grp_num_adults = fields.Integer(
        "Number of adults",
        compute="_compute_ind_grp_num_adults",
        store=True,
        recompute_daily=True,
    )
    z_ind_grp_num_adults_woman = fields.Integer(
        "Number of adults woman",
        compute="_compute_ind_grp_num_adults_woman",
        store=True,
        recompute_daily=True,
    )
    z_ind_grp_num_elderly = fields.Integer(
        "Number of eldery",
        compute="_compute_ind_grp_num_eldery",
        store=True,
        recompute_daily=True,
    )

    z_ind_grp_is_hh_with_children = fields.Boolean(
        "Is household (HH) with children",
        compute="_compute_ind_grp_is_hh_with_children",
        store=True,
        recompute_daily=True,
    )

    # z_ind_grp_is_hh_with_disabled = fields.Boolean("HHs with disabled (mental or physical) members",
    #                                                compute="_compute_ind_grp_is_hh_with_disabled")

    z_ind_grp_is_hh_with_elderly = fields.Boolean(
        "Is household with elderly",
        compute="_compute_ind_grp_is_hh_with_elderly",
        help="Households (HH) with elderly (including single / elderly-headed "
        "HHs) - extracted from demographic data of HH adult members",
        store=True,
        recompute_daily=True,
    )

    z_ind_grp_is_hh_with_pregnant_lactating = fields.Boolean(
        "Is household with pregnant/lactating women",
        compute="_compute_ind_grp_is_hh_with_pregnant_lactating",
        help="HH with pregnant/lactating women",
        store=True,
    )

    z_ind_grp_is_hh_with_disabled = fields.Boolean(
        "Is household disabled (mental or physical) members",
        compute="_compute_ind_grp_is_hh_with_disabled",
        help="HHs with disabled (mental or physical) members",
        store=True,
    )

    z_ind_grp_is_hh_with_medical_condition = fields.Boolean(
        "Is household with members that have chronic illness/medical conditions",
        compute="_compute_ind_grp_is_hh_with_medical_condition",
        help="HHs with members that have chronic illness/medical conditions",
        store=True,
    )

    z_ind_grp_is_single_head_hh = fields.Boolean(
        "Is single-headed household",
        compute="_compute_ind_grp_is_single_head_hh",
        help="Single-headed HH - extracted from demographic data of " "HH adult members",
        store=True,
    )
    z_ind_grp_is_woman_head_hh = fields.Boolean(
        "Is female-headed household",
        compute="_compute_ind_grp_is_woman_head_hh",
        help="Female-headed HH - extracted from demographic data of " "HH adult members",
        store=True,
    )
    z_ind_grp_is_elderly_head_hh = fields.Boolean(
        "Is elderly-headed household",
        compute="_compute_ind_grp_is_eldery_head_hh",
        help="Elderly-headed HHs - " "extracted from demographic data of HH adult members",
        store=True,
        recompute_daily=True,
    )

    def _compute_ind_grp_num_children(self):
        """
        Households (HH) with children
        Returns:
        """
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)
        domain = [("birthdate", ">=", children)]
        self.compute_count_and_set_indicator("z_ind_grp_num_children", None, domain)

    def _compute_ind_grp_num_children_12_and_above(self):
        """
        Households (HH) with children aged above 12
        :return:
        """
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)
        domain = [
            ("birthdate", ">=", children),
            ("birthdate", "<", now - relativedelta(years=12)),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_num_children_12_and_above", None, domain)

    def _compute_ind_grp_num_children_11_and_below(self):
        """
        Households (HH) with children aged 11 and below
        :return:
        """
        now = datetime.datetime.now()
        domain = [
            ("birthdate", ">", now - relativedelta(years=12)),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_num_children_11_and_below", None, domain)

    def _compute_ind_grp_num_eldery(self):
        """
        Number of Eldery in this household
        Returns:
        """
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_num_elderly", None, domain)

    def _compute_ind_grp_num_members(self):
        """
        Number of members in this household
        Returns:
        """
        self.compute_count_and_set_indicator("z_ind_grp_num_members", None, [])

    def _compute_ind_grp_num_adults(self):
        """
        Number of adults in this household
        Returns:
        """
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_num_adults", None, domain)

    def _compute_ind_grp_num_adults_woman(self):
        """
        Number of adults woman in this household
        Returns:
        """
        now = datetime.datetime.now()
        domain = [
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Female"),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_num_adults_woman", None, domain)

    def _compute_ind_grp_is_single_head_hh(self):
        """
        single-headed HH - extracted from demographic data of HH adult members
        Returns:
        """
        # TODO: Should we exclude eldery?
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_is_single_head_hh", None, domain, presence_only=True)

    def _compute_ind_grp_is_woman_head_hh(self):
        """
        female-headed HH - extracted from demographic data of HH adult members
        Returns:
        """
        _logger.info("-" * 80)
        _logger.info("_compute_ind_grp_is_woman_head_hh")
        _logger.info("self: %s", self)
        now = datetime.datetime.now()
        domain = [
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Female"),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_is_woman_head_hh", ["Head"], domain, presence_only=True)

    def _compute_ind_grp_is_eldery_head_hh(self):
        """
        Elderly-headed HHs - extracted from demographic
        data of HH adult members
        Returns:
        """
        _logger.info("-" * 80)
        _logger.info("_compute_ind_grp_is_eldery_head_hh")
        _logger.info("self: %s", self)
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_is_elderly_head_hh", ["Head"], domain, presence_only=True)

    def _compute_ind_grp_is_hh_with_children(self):
        """
        Households (HH) with children - extracted from demographic data of HH adult members
        plus child members from personal data
        """
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)
        domain = [("birthdate", ">=", children)]
        self.compute_count_and_set_indicator("z_ind_grp_is_hh_with_children", None, domain, presence_only=True)

    def _compute_ind_grp_is_hh_with_pregnant_lactating(self):
        """
        Households (HH) with pregnant and lactating
        """
        datetime.datetime.now()
        domain = [
            "|",
            ("z_cst_indv_pregnancy_start", "!=", None),
            ("z_cst_indv_lactation_start", "=", None),
        ]
        self.compute_count_and_set_indicator(
            "z_ind_grp_is_hh_with_pregnant_lactating",
            None,
            domain,
            presence_only=True,
        )

    def _compute_ind_grp_is_hh_with_disabled(self):
        """
        HHs with disabled (mental or physical) members
        """
        domain = [("z_cst_indv_disability_level", ">", 0)]
        self.compute_count_and_set_indicator("z_ind_grp_is_hh_with_disabled", None, domain, presence_only=True)

    def _compute_ind_grp_is_hh_with_medical_condition(self):
        """
        HHs with members that have chronic illness/medical conditions
        """
        domain = [("z_cst_indv_medical_condition", ">", 0)]
        self.compute_count_and_set_indicator(
            "z_ind_grp_is_hh_with_medical_condition",
            None,
            domain,
            presence_only=True,
        )

    def _compute_ind_grp_is_hh_with_elderly(self):
        """
        Households (HH) with elderly - extracted from demographic data of HH adult members
        plus elderly members from personal data
        """
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_is_hh_with_elderly", None, domain, presence_only=True)
