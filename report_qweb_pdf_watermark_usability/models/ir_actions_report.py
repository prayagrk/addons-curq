import json

from odoo import models

PARAM_KEY = "report_qweb_pdf_watermark_usability.outgoing_report_config_ids"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _register_hook(self):
        res = super()._register_hook()
        param = self.env["ir.config_parameter"].sudo().get_param(PARAM_KEY)
        report_ids = []
        if param:
            try:
                report_ids = json.loads(param)
            except (ValueError, TypeError):
                report_ids = []

        if report_ids:
            reports = self.env["ir.actions.report"].browse(report_ids).exists()
            reports.filtered(lambda r: not r.use_company_watermark).write(
                {"use_company_watermark": True}
            )
        return res
