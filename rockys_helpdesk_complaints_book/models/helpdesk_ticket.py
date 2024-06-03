from odoo import fields,models,api,_

class HDTicket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    is_complaints_book = fields.Boolean(string='¿Es ticket del libro de reclamaciones?',compute='_compute_is_complaints_book',store=True)
    # [1] ELECCIÓN DEL RESTAURANTE
    #restaurant_id = fields.Many2one('helpdesk.tienda',string='Restaurante')
    business_name = fields.Char('Razón Social')
    ruc = fields.Char('RUC')
    fiscal_address = fields.Char('Dirección fiscal')
    # [2] IDENTIFICACIÓN DEL CONSUMIDOR RECLAMANTE
    claimant_id = fields.Many2one('res.partner',string='Reclamate')
    claimant_department_id = fields.Char('Departamento')
    claimant_address = fields.Char('Dirección')
    claimant_identification_document = fields.Char('DNI/C.E.')
    claimant_phone = fields.Char('Teléfono')
    claimant_cell_phone = fields.Char('Celular')
    claimant_email = fields.Char('Correo electrónico')
    #Para el caso de menores de edad deberá registrarse adicionalmente el nombre del padre/madre
    parent_ct_id = fields.Many2one('res.partner',string='Padre/Madre')
    parent_ct_identification_document = fields.Char('DNI')
    parent_ct_phone = fields.Char('Teléfono')
    parent_ct_address = fields.Char('Dirección')
    parent_ct_email = fields.Char('Correo electrónico')
    # [3] IDENTIFICACIÓN DEL PRODUCTO O SERVICIO CONTRATADO
    contracted_type = fields.Selection([('product','Producto'),('service','Servicio')],string='Tipo')
    order_number = fields.Char('Número del pedido')
    order_date = fields.Date('Fecha del pedido')
    order_channel_id = fields.Many2one('helpdesk.ticket.channel',string='Canal del pedido')
    reclaimed_amount = fields.Float('Monto reclamado')
    order_detail = fields.Html('Detalle del pedido')
    # [4] DETALLE RECLAMCIÓN Y PEDIDO DEL CONSUMIDOR
    type_claim = fields.Selection([('claim','Reclamo'),('complaint','Queja')],string='Tipo')
    claim_detail = fields.Html('Detalle del reclamo o queja')
    # [5] OBSERVACIONES Y ACCIONES ADOPTADAS POR EL PROVEEDOR
    action_date = fields.Date('Fecha')
    action_detail = fields.Html('Detalle')
    
    @api.depends('team_id','ticket_type_id')
    def _compute_is_complaints_book(self):
        for record in self:
            record.is_complaints_book = True if record.team_id.id == self.env.ref('rockys_helpdesk_complaints_book.helpdesk_claims_book_equipment').id and record.ticket_type_id.id == self.env.ref('rockys_helpdesk_complaints_book.type_claim_or_complaint').id else False