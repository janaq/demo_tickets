from odoo import fields,models,api,_

class XTienda(models.Model):
    
    _inherit = 'helpdesk.tienda'
    
    brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca')