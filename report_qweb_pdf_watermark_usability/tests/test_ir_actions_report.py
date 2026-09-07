from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrActionsReportHook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["ir.actions.report"]

    def test_register_hook_updates_watermark_flag(self):
        sample_xml_id = "account.account_invoices"
        report = self.env.ref(sample_xml_id, raise_if_not_found=False)

        if not report:
            report = self.Report.create(
                {
                    "name": "Test Invoice Report",
                    "model": "res.partner",
                    "report_type": "qweb-pdf",
                    "report_name": "test.invoice_report",
                    "use_company_watermark": False,
                }
            )
            self.env["ir.model.data"].create(
                {
                    "name": "account_invoices",
                    "module": "account",
                    "model": "ir.actions.report",
                    "res_id": report.id,
                }
            )
        else:
            report.use_company_watermark = False

        self.env["res.config.settings"].add_watermark_reports([sample_xml_id])
        report.use_company_watermark = False
        self.assertFalse(report.use_company_watermark)

        self.Report._register_hook()

        self.assertTrue(
            report.use_company_watermark,
            "The hook should update use_company_watermark to True.",
        )

    def test_register_hook_missing_xml_ids_handled_gracefully(self):
        with patch.object(
            self.Report.__class__,
            "_register_hook",
            wraps=self.Report._register_hook,
        ):
            try:
                self.Report._register_hook()
            except Exception as e:
                self.fail(f"_register_hook raised an unexpected exception: {e}")

    def test_register_hook_unrelated_reports_untouched(self):
        other_report = self.Report.create(
            {
                "name": "Custom Internal Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "test.custom_report",
                "use_company_watermark": False,
            }
        )

        self.Report._register_hook()

        self.assertFalse(
            other_report.use_company_watermark,
            "Reports not listed in config should retain their original watermark state.",
        )

    def test_register_hook_preserves_already_true_reports(self):
        report = self.Report.create(
            {
                "name": "Test Active Watermark Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "test.active_report",
                "use_company_watermark": True,
            }
        )
        self.Report._register_hook()
        self.assertTrue(report.use_company_watermark)

    def test_res_config_settings_set_and_get_values(self):
        test_report = self.Report.create(
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

    def test_add_watermark_reports_missing_xml_ids(self):
        try:
            self.env["res.config.settings"].add_watermark_reports(
                ["non_existent.report_action"]
            )
        except Exception as e:
            self.fail(f"add_watermark_reports raised an unexpected exception: {e}")
