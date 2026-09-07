from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrActionsReportHook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["ir.actions.report"]

    def test_register_hook_updates_watermark_flag(self):
        """Existing reports in outgoing_reports should have use_company_watermark set to True."""
        sample_xml_id = "account.account_invoices"
        report = self.env.ref(sample_xml_id, raise_if_not_found=False)

        if not report:
            # Fallback: dynamically create an ir.model.data record to simulate the target report
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

        self.assertFalse(report.use_company_watermark)

        self.Report._register_hook()

        self.assertTrue(
            report.use_company_watermark,
            "The hook should update use_company_watermark to True.",
        )

    def test_register_hook_missing_xml_ids_handled_gracefully(self):
        """Missing XML IDs (uninstalled modules) should not raise errors."""
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
        """Reports outside the target list must remain untouched."""
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
            "Reports not listed in outgoing_reports should retain their original watermark state.",
        )

    def test_register_hook_preserves_already_true_reports(self):
        """Reports that already have use_company_watermark=True remain unchanged."""
        sample_xml_id = "sale.action_report_saleorder"
        report = self.env.ref(sample_xml_id, raise_if_not_found=False)

        if report:
            report.use_company_watermark = True
            self.Report._register_hook()
            self.assertTrue(report.use_company_watermark)
