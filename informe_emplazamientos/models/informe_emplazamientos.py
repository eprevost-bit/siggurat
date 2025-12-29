from odoo import models, fields, tools


class EmplacementRevenueReport(models.Model):
    _name = "mp.emplacement.revenue.report"
    _description = "Informe de Ingresos por Emplazamiento"
    _auto = False  # Importante: Esto indica que es una vista SQL
    _rec_name = 'emplacement_id'

    # Campos que quieres ver en el informe
    emplacement_id = fields.Many2one('mp.site.emplacement', string="Emplazamiento", readonly=True)
    state_id = fields.Many2one('res.country.state', string="Provincia", readonly=True)
    sale_id = fields.Many2one('sale.order', string="Pedido de Venta", readonly=True)
    currency_id = fields.Many2one('res.currency', string="Moneda", readonly=True)
    revenue = fields.Monetary(string="Ingreso Generado", currency_field='currency_id', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER() AS id,
                    s.id AS sale_id,
                    e.id AS emplacement_id,
                    e.state_id AS state_id,
                    s.currency_id AS currency_id,
                    s.amount_total AS revenue,
                    s.company_id AS company_id
                FROM
                    sale_order s

                -- 1. Unimos Venta con la tabla intermedia (Many2many)
                -- IMPORTANTE: Verifica que este nombre 'sale_order_mp_site_ad_space_rel' sea el correcto
                -- Mirando el campo 'Relation' en la configuración del campo ad_space_id
                JOIN
                    sale_order_mp_site_ad_space_rel rel ON s.id = rel.sale_order_id

                -- 2. Unimos la intermedia con el Espacio Publicitario (mp.site.ad.space)
                -- Verifica si la columna se llama 'mp_site_ad_space_id' o 'ad_space_id' en la tabla rel
                JOIN
                    mp_site_ad_space ads ON rel.mp_site_ad_space_id = ads.id

                -- 3. Unimos el Espacio con el Emplazamiento (mp.site.emplacement)
                -- Asumo que el mp.site.ad.space tiene un campo 'emplacement_id' o similar
                JOIN
                    mp_site_emplacement e ON ads.mp_site_emplacement_id = e.id

                WHERE
                    s.state IN ('sale', 'done')
                    AND s.subscription_state = '3_progress'
            )
        """ % self._table)