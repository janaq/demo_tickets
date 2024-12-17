from odoo import fields,models,api,_

class XTienda(models.Model):
    
    _inherit = 'helpdesk.tienda'
    
    brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca')
    image = fields.Binary(string='Imagen',compute='_compute_image',store=True,readonly=False)
    
    @api.depends(
        'brand_id',
        'brand_id.logo'
    )
    def _compute_image(self):
        for record in self:
            image = False if not record.brand_id else record.brand_id.logo
            record.sudo().write({'image':image})
                