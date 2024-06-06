from odoo import fields,models,api,_

class HDTicketChannel(models.Model):
    
    _name = 'helpdesk.ticket.channel'
    _description = 'Canal del pedido'
    
    name = fields.Char('Nombre')
    description = fields.Char('Descripción')
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company.id)
    