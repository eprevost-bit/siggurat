from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class AccountReportBudgetItem(models.Model):
    _inherit = 'account.report.budget.item'

    last_year_balance = fields.Float(
        string="Saldo Año Anterior",
        compute="_compute_budget_logic",
        store=True
    )
    percentage_adj = fields.Float(string="% Incremento")

    @api.depends('account_id', 'date', 'percentage_adj')
    def _compute_budget_logic(self):
        for record in self:
            if record.account_id and record.date:
                # Calculamos el rango de fechas del año anterior
                prev_year_date = record.date - relativedelta(years=1)
                date_from = prev_year_date.replace(day=1)
                date_to = prev_year_date + relativedelta(day=31)

                # Buscamos los apuntes contables (account.move.line) de ese periodo
                domain = [
                    ('account_id', '=', record.account_id.id),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('move_id.state', '=', 'posted')
                ]
                aml_data = self.env['account.move.line'].read_group(
                    domain, ['balance'], ['account_id']
                )

                balance = aml_data[0]['balance'] if aml_data else 0.0
                record.last_year_balance = balance

                # Aplicamos la fórmula: Cantidad anterior + (Cantidad anterior * %)
                # Usamos / 100.0 para que si el usuario pone "10", sea el 10%
                increment = balance * (record.percentage_adj / 100.0)
                record.amount = balance + increment
            else:
                record.last_year_balance = 0.0