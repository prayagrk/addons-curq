from odoo import Command, api, fields, models

<<<<<<< HEAD
CONFIG_PARAM_WATERMARK_REPORTS = (
    "report_qweb_pdf_watermark_usability.outgoing_report_config_ids"  # noqa
)

=======
>>>>>>> d84f05d ([ADD] report_qweb_pdf_watermark_usability)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    outgoing_report_config_ids = fields.Many2many(
        "ir.actions.report",
        string="Outgoing Reports",
        domain="[('report_type', '=', 'qweb-pdf')]",
    )

<<<<<<< HEAD
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list, strict=False):
            if "outgoing_report_config_ids" in vals:
                record.set_values()
        return records

    @api.model
    def _get_watermark_report_ids(self):
        """Retrieve configured watermark report IDs
        from ir.config_parameter as a set."""
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(CONFIG_PARAM_WATERMARK_REPORTS, "")
        )
        return {int(i) for i in param.split(",") if i.strip().isdigit()}

    def set_values(self):  # pylint: disable=missing-return
        prev_report_ids = self._get_watermark_report_ids()
        super().set_values()

        selected_reports = self.outgoing_report_config_ids.filtered(
            lambda r: r.report_type == "qweb-pdf"
        )
        selected_report_ids = set(selected_reports.ids)

        if self.env.context.get("watermark_append_mode"):
            # For child modules.
            if selected_report_ids:
                self.add_watermark_reports(list(selected_report_ids))

            all_report_ids = prev_report_ids | selected_report_ids
            active_reports = (
                self.env["ir.actions.report"]
                .browse(all_report_ids)
                .exists()
                .filtered(
                    lambda r: r.report_type == "qweb-pdf" and r.use_company_watermark
                )
            )
            self.env["ir.config_parameter"].sudo().set_param(
                CONFIG_PARAM_WATERMARK_REPORTS,
                ",".join(str(i) for i in sorted(active_reports.ids)),
            )
        else:
            # For regular UI save.
            reports_to_disable_ids = prev_report_ids - selected_report_ids
            if reports_to_disable_ids:
                reports_to_disable = (
                    self.env["ir.actions.report"]
                    .browse(reports_to_disable_ids)
                    .exists()
                )
                reports_to_disable.write({"use_company_watermark": False})

            reports_to_enable_ids = selected_report_ids - prev_report_ids
            if reports_to_enable_ids:
                self.add_watermark_reports(list(reports_to_enable_ids))

            active_selected_reports = selected_reports.filtered(
                lambda r: r.use_company_watermark
            )
            self.env["ir.config_parameter"].sudo().set_param(
                CONFIG_PARAM_WATERMARK_REPORTS,
                ",".join(str(i) for i in sorted(active_selected_reports.ids)),
            )
=======
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
>>>>>>> d84f05d ([ADD] report_qweb_pdf_watermark_usability)

    @api.model
    def get_values(self):
        res = super().get_values()
<<<<<<< HEAD
        active_reports = (
            self.env["ir.actions.report"]
            .browse(self._get_watermark_report_ids())
            .exists()
            .filtered(lambda r: r.report_type == "qweb-pdf" and r.use_company_watermark)
=======
        active_reports = self.env["ir.actions.report"].search(
            [
                ("report_type", "=", "qweb-pdf"),
                ("use_company_watermark", "=", True),
                ("pdf_watermark", "=", False),
                ("pdf_watermark_expression", "=", False),
            ]
>>>>>>> d84f05d ([ADD] report_qweb_pdf_watermark_usability)
        )
        res["outgoing_report_config_ids"] = [Command.set(active_reports.ids)]
        return res

    @api.model
    def add_watermark_reports(self, report_ids):
<<<<<<< HEAD
        """Enable company watermark on reports specified by a list of IDs."""
        if not isinstance(report_ids, list):
            raise TypeError(
                f"report_ids must be a list of integer IDs, got "
                f"{type(report_ids).__name__}"
            )
        if not report_ids:
            return

        reports = (
            self.env["ir.actions.report"]
            .browse([rid for rid in report_ids if rid])
            .exists()
        )
=======
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
>>>>>>> d84f05d ([ADD] report_qweb_pdf_watermark_usability)

        reports_to_enable = reports.filtered(
            lambda r: r.report_type == "qweb-pdf"
            and not r.use_company_watermark
            and not r.pdf_watermark
            and not r.pdf_watermark_expression
        )
        if reports_to_enable:
            reports_to_enable.write({"use_company_watermark": True})
