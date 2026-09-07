import json

from odoo import Command, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    outgoing_report_config_ids = fields.Many2many(
        "ir.actions.report",
        string="Outgoing Report",
    )

    def set_values(self):
        old_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("report_qweb_pdf_watermark_usability.outgoing_report_config_ids")
        )
        try:
            old_ids = set(json.loads(old_param)) if old_param else set()
        except (ValueError, TypeError):
            old_ids = set()

        res = super(ResConfigSettings, self).set_values()

        new_ids = set(self.outgoing_report_config_ids.ids)
        self.env["ir.config_parameter"].sudo().set_param(
            "report_qweb_pdf_watermark_usability.outgoing_report_config_ids",
            json.dumps(list(new_ids)),
        )

        Report = self.env["ir.actions.report"]

        added_ids = new_ids - old_ids
        if added_ids:
            Report.browse(list(added_ids)).exists().filtered(
                lambda r: not r.use_company_watermark
            ).write({"use_company_watermark": True})

        removed_ids = old_ids - new_ids
        if removed_ids:
            Report.browse(list(removed_ids)).exists().filtered(
                lambda r: r.use_company_watermark
            ).write({"use_company_watermark": False})
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("report_qweb_pdf_watermark_usability.outgoing_report_config_ids")
        )
        ids = []
        if param:
            try:
                ids = json.loads(param)
            except (ValueError, TypeError):
                ids = []
        valid_ids = self.env["ir.actions.report"].browse(ids).exists().ids
        res.update(outgoing_report_config_ids=[Command.set(valid_ids)])
        return res

    @api.model
    def add_watermark_reports(self, xml_ids):
        param_key = "report_qweb_pdf_watermark_usability.outgoing_report_config_ids"
        old_param = self.env["ir.config_parameter"].sudo().get_param(param_key)
        try:
            existing_ids = set(json.loads(old_param)) if old_param else set()
        except (ValueError, TypeError):
            existing_ids = set()

        new_report_ids = set()
        for xml_id in xml_ids:
            report = self.env.ref(xml_id, raise_if_not_found=False)
            if report:
                new_report_ids.add(report.id)

        merged_ids = existing_ids | new_report_ids
        self.env["ir.config_parameter"].sudo().set_param(
            param_key, json.dumps(list(merged_ids))
        )

        added_ids = new_report_ids - existing_ids
        if added_ids:
            self.env["ir.actions.report"].browse(list(added_ids)).exists().filtered(
                lambda r: not r.use_company_watermark
            ).write({"use_company_watermark": True})
