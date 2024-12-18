from odoo import fields,models,api,_

class XTienda(models.Model):
    
    _inherit = 'helpdesk.tienda'
    
    brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca')
    image = fields.Image(string='Imagen',compute='_compute_image',store=True,readonly=False)
    color = fields.Char(default="#dcd6d6",compute='_compute_color', help="Color de la tienda para la visualización del correo electrónico",readonly=False,store=True)
    
    @api.depends(
        'brand_id',
        'brand_id.image'
    )
    def _compute_image(self):
        for record in self:
            image = False if not record.brand_id else record.brand_id.image
            record.sudo().write({'image':image})
            
    @api.depends(
        'brand_id',
        'brand_id.color'
    )
    def _compute_color(self):
        for record in self:
            color = "#dcd6d6" if not record.brand_id else record.brand_id.color
            record.sudo().write({'color':color})
                