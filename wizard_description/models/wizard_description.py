# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleDescriptionWizard(models.TransientModel):
    _name = 'sale.description.update.wizard'
    _description = 'Wizard para actualizar descripciones de líneas'

    def action_confirm(self):
        # Obtenemos los pedidos seleccionados desde el contexto
        order_ids = self.env.context.get('active_ids')
        orders = self.env['sale.order'].browse(order_ids)

        for order in orders:
            for line in order.order_line:
                # 1. Verificamos que la línea tenga un producto y un espacio vinculado
                # Reemplaza 'x_studio_espacio_id' por el nombre técnico de tu campo link
                espacio = getattr(line, 'x_studio_espacio_id', False)

                if espacio:
                    # 2. Extraemos los datos del modelo mp.site.ad.space
                    prod_name = line.product_id.display_name or ''
                    espacio_name = espacio.name or ''
                    ubicacion = espacio.ubication or ''  # Ajustar si el campo se llama distinto
                    via = espacio.way or ''  # Ajustar si el campo se llama distinto

                    # 3. Construimos el bloque de texto con saltos de línea (\n)
                    nueva_descripcion = f"{prod_name}\n{espacio_name}\n{ubicacion}\n{via}"

                    # 4. Actualizamos la línea
                    line.write({
                        'name': nueva_descripcion
                    })
        return {'type': 'ir.actions.act_window_close'}