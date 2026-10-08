from odoo import Command, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    outgoing_report_config_ids = fields.Many2many(
        "ir.actions.report",
        string="Outgoing Reports",
        domain="[('report_type', '=', 'qweb-pdf')]",
    )

    def set_values(self):
        res = super().set_values()
        active_reports = self.env["ir.actions.report"].search(
            [
                ("report_type", "=", "qweb-pdf"),
                ("use_company_watermark", "=", True),
                ("pdf_watermark", "=", False),
                ("pdf_watermark_expression", "=", False),
            ]
        )
        selected_reports = self.outgoing_report_config_ids.filtered(
            lambda r: r.report_type == "qweb-pdf"
        )
        reports_to_disable = active_reports - selected_reports
        if reports_to_disable:
            reports_to_disable.write({"use_company_watermark": False})

        self.add_watermark_reports(self.outgoing_report_config_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        active_reports = self.env["ir.actions.report"].search(
            [
                ("report_type", "=", "qweb-pdf"),
                ("use_company_watermark", "=", True),
                ("pdf_watermark", "=", False),
                ("pdf_watermark_expression", "=", False),
            ]
        )
        res["outgoing_report_config_ids"] = [Command.set(active_reports.ids)]
        return res

    @api.model
    def add_watermark_reports(self, report_ids):
        """Enable company watermark on reports specified by IDs
        (called during child module installation)."""
        if not report_ids:
            return
        if hasattr(report_ids, "ids"):
            report_ids = report_ids.ids
        elif isinstance(report_ids, int):
            report_ids = [report_ids]

        reports = self.env["ir.actions.report"]
        for report_id in report_ids:
            if report_id:
                record = self.env["ir.actions.report"].browse(report_id)
                if record.exists():
                    reports |= record

        reports_to_enable = reports.filtered(
            lambda r: r.report_type == "qweb-pdf"
            and not r.use_company_watermark
            and not r.pdf_watermark
            and not r.pdf_watermark_expression
        )
        if reports_to_enable:
            reports_to_enable.write({"use_company_watermark": True})
