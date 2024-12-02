from odoo.tests.common import TransactionCase


class TestGenerateGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.generate_data_id = cls.env["spp.generate.data"].create(
            {
                "num_groups": 5,
                "name": "Test Generate Group",
            }
        )

    def test_job_queue_generate_sample_data(self):
        current_count = len(self.env["queue.job"].search([]))
        self.generate_data_id.generate_sample_data()

        self.assertEqual(len(self.env["queue.job"].search([])), current_count + 1)

        queue_job_id = self.env["queue.job"].search([], order="date_created DESC", limit=1)

        self.assertEqual(queue_job_id.model_name, "spp.generate.data")
        self.assertEqual(queue_job_id.state, "pending")
        self.assertEqual(queue_job_id.channel_method_name, "<spp.generate.data>._generate_sample_data")

    def test_generate_sample_data(self):
        current_count = len(self.env["res.partner"].search([("is_group", "=", True)]))
        self.env["spp.generate.data"]._generate_sample_data(res_id=self.generate_data_id.id)

        self.assertEqual(
            len(self.env["res.partner"].search([("is_group", "=", True)])),
            current_count + self.generate_data_id.num_groups,
        )
