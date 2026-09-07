from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _register_hook(self):
        res = super()._register_hook()
        outgoing_reports = [
            # Invoicing & Accounting
            "account.account_invoices",
            "account.account_invoices_without_payment",
            "account.action_report_payment_receipt",
            # Sales & Quotations
            "sale.action_report_saleorder",
            "sale.action_report_pro_forma_invoice",
            "sale_pdf_quote_builder.action_report_saleorder_raw",
            # Delivery & Logistics
            "stock.action_report_delivery",
            "stock.stock_reception_report_action",
            "stock.return_label_report",
            # Repairs
            "repair.action_report_repair_order",
            # Services, Timesheets & Field Service
            "sale_timesheet.timesheet_report_sale_order",
            "sale_timesheet.timesheet_report_account_move",
            # Point of Sale & Events
            "event.action_report_event_registration_badge",
        ]
        for xml_id in outgoing_reports:
            report = self.env.ref(xml_id, raise_if_not_found=False)
            if report and not report.use_company_watermark:
                report.use_company_watermark = True
        return res
