from odoo import models, fields, api
from datetime import date


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
                # 1. Obtener el año anterior completo

                last_year = record.date.year - 1
                date_from = date(last_year, 1, 1)
                date_to = date(last_year, 12, 31)

                # 2. Buscamos todos los apuntes del año completo
                domain = [
                    ('account_id', '=', record.account_id.id),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('move_id.state', '=', 'posted')
                ]

                # Sumamos el campo 'balance' (débito - crédito)
                aml_data = self.env['account.move.line'].read_group(
                    domain, ['balance'], ['account_id']
                )

                # 3. Tratamiento del Saldo
                # En Odoo, las cuentas de ingresos (como la 700 de tu foto) tienen saldo negativo.
                # Multiplicamos por -1 para que en el presupuesto aparezca como valor positivo.
                raw_balance = aml_data[0]['balance'] if aml_data else 0.0

                # Invertimos el signo para que coincida con la lógica de presupuesto (Ingresos = Positivo)
                total_last_year = 1 * raw_balance
                record.last_year_balance = total_last_year

                # 4. Cálculo del nuevo importe: Saldo Anterior + (Saldo Anterior * %)
                increment = total_last_year * (record.percentage_adj / 100.0)
                record.amount = total_last_year + increment
            else:
                record.last_year_balance = 0.0
                record.amount = 0.0