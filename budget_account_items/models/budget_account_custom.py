from odoo import models, fields, api
from datetime import date

from odoo.tools import float_is_zero


class AccountReportBudgetItem(models.Model):
    _inherit = 'account.report.budget.item'

    last_year_balance = fields.Float(
        string="Saldo Año Anterior",
        compute="_compute_budget_logic",
        store=True,
        copy=True,
        digits=(16, 2)
    )

    # Nuevo campo solo para la VISTA (Front-end)
    last_year_balance_ui = fields.Float(
        string="Saldo Año Ant.",
        compute="_compute_balance_ui",
        store=True,
        copy=True,
        digits = (16, 2)
    )

    amount = fields.Float(
        string="Importe",
        compute="_compute_budget_logic",
        store=True,
        readonly=False  # Permite edición manual si lo prefieres
    )

    amouunt_ui = fields.Float(
        string='Importe',
        compute="_compute_importe_ui",
        inverse="_inverse_importe_ui",  # Permite que lo que escribas se guarde
        store=False,
        readonly=False,
        digits=(16, 2)
    )

    def _inverse_importe_ui(self):
        for record in self:
            # Si escribes 1230 en la UI, guardamos -1230 en amount
            record.amount = record.amouunt_ui * -1

    @api.onchange('amouunt_ui')
    def _onchange_amouunt_ui(self):
        # Primero actualizamos el valor real para el cálculo
        real_amount = self.amouunt_ui * -1
        self.amount = real_amount

        # Calculamos el porcentaje igual que antes
        if self.last_year_balance and self.last_year_balance != 0:
            # Importante: Usamos el signo real para el cálculo matemático
            self.percentage_adj = (real_amount / self.last_year_balance) - 1

    @api.depends('amount')
    def _compute_importe_ui(self):
        for record in self:
            if float_is_zero(record.amount, precision_digits=2):
                record.amouunt_ui = 0.0
            else:
                inverted = round(record.amount * -1, 2)
                # Limpieza de signo para el cero
                record.amouunt_ui = 0.0 if inverted == -0.0 else inverted

    @api.depends('last_year_balance')
    def _compute_balance_ui(self):
        for record in self:
            # Invertimos el signo: si es -5 muestra 5, si es 5 muestra -5
            record.last_year_balance_ui = record.last_year_balance * -1

    # Redefinimos amount para que dependa de nuestra lógica

    percentage_adj = fields.Float(string="% Incremento", default=0.0)

    @api.depends('account_id', 'date', 'percentage_adj')
    def _compute_budget_logic(self):
        for record in self:
            if record.account_id and record.date:
                # 1. Obtener el rango del año anterior
                last_year = record.date.year - 1
                date_from = date(last_year, 1, 1)
                date_to = date(last_year, 12, 31)

                # 2. Búsqueda de apuntes contables
                domain = [
                    ('account_id', '=', record.account_id.id),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('move_id.state', '=', 'posted')
                ]

                # Usamos read_group para eficiencia
                aml_data = self.env['account.move.line'].read_group(
                    domain, ['balance'], ['account_id']
                )

                # 3. Tratamiento del Saldo
                # Odoo devuelve saldo negativo para ingresos.
                # Si quieres que ingresos sean positivos, asegúrate de la lógica de signo:
                raw_balance = aml_data[0]['balance'] if aml_data else 0.0

                # Para presupuestos de ingresos, solemos invertir el signo
                total_last_year = raw_balance
                record.last_year_balance = total_last_year

                incremento = total_last_year * record.percentage_adj
                record.amount = total_last_year + incremento

            else:
                record.last_year_balance = 0.0
                record.amount = 0.0

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.last_year_balance and self.last_year_balance != 0:
            self.percentage_adj = (self.amount / self.last_year_balance) - 1

# from odoo import models, fields, api
# from datetime import date
#
#
# class AccountReportBudgetItem(models.Model):
#     _inherit = 'account.report.budget.item'
#
#     last_year_balance = fields.Float(
#         string="Saldo Año Anterior",
#         compute="_compute_budget_logic",
#         store=True
#     )
#     percentage_adj = fields.Float(string="% Incremento")
#
#     @api.depends('account_id', 'date', 'percentage_adj')
#     def _compute_budget_logic(self):
#         for record in self:
#             if record.account_id and record.date:
#                 # 1. Obtener el año anterior completo
#
#                 last_year = record.date.year - 1
#                 date_from = date(last_year, 1, 1)
#                 date_to = date(last_year, 12, 31)
#
#                 # 2. Buscamos todos los apuntes del año completo
#                 domain = [
#                     ('account_id', '=', record.account_id.id),
#                     ('date', '>=', date_from),
#                     ('date', '<=', date_to),
#                     ('move_id.state', '=', 'posted')
#                 ]
#
#                 # Sumamos el campo 'balance' (débito - crédito)
#                 aml_data = self.env['account.move.line'].read_group(
#                     domain, ['balance'], ['account_id']
#                 )
#
#                 # 3. Tratamiento del Saldo
#                 # En Odoo, las cuentas de ingresos (como la 700 de tu foto) tienen saldo negativo.
#                 # Multiplicamos por -1 para que en el presupuesto aparezca como valor positivo.
#                 raw_balance = aml_data[0]['balance'] if aml_data else 0.0
#
#                 # Invertimos el signo para que coincida con la lógica de presupuesto (Ingresos = Positivo)
#                 total_last_year = raw_balance
#                 record.last_year_balance = total_last_year
#
#                 # 4. Cálculo del nuevo importe: Saldo Anterior + (Saldo Anterior * %)
#                 increment = total_last_year * (record.percentage_adj / 100.0)
#                 record.amount = total_last_year + increment
#             else:
#                 record.last_year_balance = 0.0
#                 record.amount = 0.0