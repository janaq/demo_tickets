from odoo import fields,models,api,_

class HDTicketBrand(models.Model):
    
    _name = 'helpdesk.ticket.brand'
    _description = 'Marca del pedido/reclamo'
    
    name = fields.Char('Nombre')
    description = fields.Char('Descripción')
    logo = fields.Image('Logo')
    color = fields.Char(default="#dcd6d6", help="Color de la marca para la visualización del correo electrónico")
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company.id)
    
            
    