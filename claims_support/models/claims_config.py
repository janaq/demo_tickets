from odoo import fields,models,api,_

class ClaimsConfig(models.Model):
    
    _name = 'claim.config'
    _description = 'Configuración de la gestión de reclamo'
    
    
    name = fields.Char(string='Punto de gestión de reclamos', help='Una identificación interna de la gestión de reclamos')
    store_id = fields.Many2one('helpdesk.tienda',string='Tienda')
    code = fields.Char(string='Código')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    # [ Protector de pantalla ]
    screen_saver_image_1920 = fields.Image('Protector de pantalla', max_width=1920, max_height=1920)
    # [ Pantalla de inicio ]
    title = fields.Char('Título')
    description = fields.Char('Descripción')
    logo_image_1920 = fields.Image('Logo',max_width=1920, max_height=1920)
    # [ Recompensas ]
    is_sending_rewards = fields.Boolean('Activar envío de recompensas')