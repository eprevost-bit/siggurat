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
                    -- Generamos un ID único combinando IDs para la vista
                    row_number() OVER() AS id,

                    s.id AS sale_id,
                    e.id AS emplacement_id,
                    e.state_id AS state_id,
                    s.currency_id AS currency_id,

                    -- AQUÍ ESTÁ EL TRUCO DEL INGRESO
                    -- Nota: Si una venta tiene 2 emplazamientos, ¿el ingreso se duplica o se divide?
                    -- En este ejemplo, mostramos el total de la venta asociado al emplazamiento.
                    s.amount_total AS revenue

                FROM
                    sale_order s
                -- Unimos con la tabla intermedia del Many2many
                -- OJO: Verifica el nombre exacto de la tabla de relación en tu base de datos.
                -- Por defecto suele ser 'nombre_modelo_origen_nombre_modelo_destino_rel' 
                -- o el nombre especificado en el campo many2many.
                -- Asumiré que el campo es 'ad_space_id' en sale.order:
                JOIN
                    sale_order_mp_site_emplacement_rel rel ON s.id = rel.sale_order_id
                JOIN
                    mp_site_emplacement e ON rel.mp_site_emplacement_id = e.id

                WHERE
                    -- Condiciones que pediste:
                    s.state IN ('sale', 'done')  -- Ventas confirmadas
                    AND s.subscription_state = '3_progress' -- En proceso
            )
        """ % self._table)