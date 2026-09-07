from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportWatermark(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["ir.actions.report"]
        cls.sample_report = cls.report.create(
            {
                "name": "Test Sample Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "test.sample_report",
                "use_company_watermark": False,
            }
        )
        cls.env["ir.model.data"].create(
            {
                "name": "test_sample_report",
                "module": "report_qweb_pdf_watermark_usability",
                "model": "ir.actions.report",
                "res_id": cls.sample_report.id,
            }
        )

    def test_add_watermark_reports(self):
        xml_id = "report_qweb_pdf_watermark_usability.test_sample_report"
        self.assertFalse(self.sample_report.use_company_watermark)

        self.env["res.config.settings"].add_watermark_reports([xml_id])
        self.assertTrue(self.sample_report.use_company_watermark)

    def test_add_watermark_reports_missing_xml_ids_handled_gracefully(self):
        try:
            self.env["res.config.settings"].add_watermark_reports(
                ["non_existent.report_action"]
            )
        except Exception as e:
            self.fail(f"add_watermark_reports raised an unexpected exception: {e}")

    def test_add_watermark_reports_ignores_non_pdf(self):
        text_report = self.report.create(
            {
                "name": "Test Text Report",
                "model": "res.partner",
                "report_type": "qweb-text",
                "report_name": "test.text_report",
                "use_company_watermark": False,
            }
        )
        self.env["ir.model.data"].create(
            {
                "name": "test_text_report",
                "module": "report_qweb_pdf_watermark_usability",
                "model": "ir.actions.report",
                "res_id": text_report.id,
            }
        )
        self.env["res.config.settings"].add_watermark_reports(
            ["report_qweb_pdf_watermark_usability.test_text_report"]
        )
        self.assertFalse(text_report.use_company_watermark)

    def test_res_config_settings_set_and_get_values(self):
        test_report = self.report.create(
            {
                "name": "Test Settings Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "test.settings_report",
                "use_company_watermark": False,
            }
        )
        settings = self.env["res.config.settings"].create(
            {"outgoing_report_config_ids": [Command.set(test_report.ids)]}
        )
        settings.set_values()
        self.assertTrue(test_report.use_company_watermark)

        values = self.env["res.config.settings"].get_values()
        self.assertIn(test_report.id, values["outgoing_report_config_ids"][0][2])

        settings = self.env["res.config.settings"].create(
            {"outgoing_report_config_ids": [Command.clear()]}
        )
        settings.set_values()
        self.assertFalse(test_report.use_company_watermark)
