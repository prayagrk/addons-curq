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
        report = self.env["ir.actions.report"]
        active_reports = report.search(
            [
                ("report_type", "=", "qweb-pdf"),
                ("use_company_watermark", "=", True),
            ]
        )
        selected_reports = self.outgoing_report_config_ids.filtered(
            lambda r: r.report_type == "qweb-pdf"
        )

        reports_to_enable = selected_reports - active_reports
        if reports_to_enable:
            reports_to_enable.write({"use_company_watermark": True})

        reports_to_disable = active_reports - selected_reports
        if reports_to_disable:
            reports_to_disable.write({"use_company_watermark": False})
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        active_reports = self.env["ir.actions.report"].search(
            [
                ("report_type", "=", "qweb-pdf"),
                ("use_company_watermark", "=", True),
            ]
        )
        res["outgoing_report_config_ids"] = [Command.set(active_reports.ids)]
        return res

    @api.model
    def add_watermark_reports(self, xml_ids):
        """Enable company watermark on reports specified by XML IDs
        (called during module installation)."""
        reports = self.env["ir.actions.report"]
        for xml_id in xml_ids:
            record = self.env.ref(xml_id, raise_if_not_found=False)
            if record and record._name == "ir.actions.report":
                reports |= record

        reports_to_enable = reports.filtered(
            lambda r: r.report_type == "qweb-pdf"
            and not r.use_company_watermark
            and not r.pdf_watermark
            and not r.pdf_watermark_expression
        )
        if reports_to_enable:
            reports_to_enable.write({"use_company_watermark": True})
