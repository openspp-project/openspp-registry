from .common import Common


class TestRegistrant(Common):
    def test_01_open_record_consent_wizard_group(self):
        consent_wiz = self._model.search([("group_id", "=", self._test_group.id)], limit=1)
        if consent_wiz:
            self.skipTest("Consent wizard already existed!")
        self._test_group.open_record_consent_wizard()
        consent_wiz = self._model.search([("group_id", "=", self._test_group.id)], limit=1)
        self.assertTrue(
            consent_wiz.is_group,
            "Consent wizard created from group should be group consent wiz!",
        )

    def test_02_open_record_consent_wizard_individual(self):
        self._test_individual_1.open_record_consent_wizard()
        consent_wiz = self._model.search([("group_id", "=", self._test_group.id)], limit=1)
        self.assertFalse(
            consent_wiz.is_group,
            "Consent wizard created from group should be group consent wiz!",
        )
