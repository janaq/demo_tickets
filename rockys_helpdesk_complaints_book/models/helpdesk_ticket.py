from odoo import fields,models,api,_

class HDTicket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    is_complaints_book = fields.Boolean(string='¿Es ticket del libro de reclamaciones?',compute='_compute_is_complaints_book',store=True)
    # [1] ELECCIÓN DEL RESTAURANTE
    #restaurant_id = fields.Many2one('helpdesk.tienda',string='Restaurante')
    business_name = fields.Char('Razón Social',tracking=True)
    ruc = fields.Char('RUC',tracking=True)
    fiscal_address = fields.Char('Dirección fiscal',tracking=True)
    # [2] IDENTIFICACIÓN DEL CONSUMIDOR RECLAMANTE
    claimant_id = fields.Many2one('res.partner',string='Reclamate',tracking=True)
    claimant_department_id = fields.Many2one('res.country.state',string='Departamento',tracking=True)
    claimant_address = fields.Char('Dirección',tracking=True)
    claimant_identification_document = fields.Char('DNI/C.E.',tracking=True)
    claimant_phone = fields.Char('Teléfono',tracking=True)
    claimant_cell_phone = fields.Char('Celular',tracking=True)
    claimant_email = fields.Char('Correo electrónico',tracking=True)
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
            record.is_complaints_book = False
            type_claim_or_complaint = self.env.ref('rockys_helpdesk_complaints_book.type_claim_or_complaint',False)
            type_claim_or_complaint = type_claim_or_complaint.id if type_claim_or_complaint else False 
            claims_book_equipment = self.env.ref('rockys_helpdesk_complaints_book.helpdesk_claims_book_equipment',False)
            claims_book_equipment = claims_book_equipment.id if claims_book_equipment else False
            if record.team_id and record.ticket_type_id \
                and type_claim_or_complaint and claims_book_equipment:
                record.is_complaints_book = True if record.team_id.id == claims_book_equipment and record.ticket_type_id.id == type_claim_or_complaint else False
            
    @api.onchange('store_id')
    def onchange_store_id(self):
        for record in self:
            store_id = record.store_id
            record.business_name = store_id.business_name if store_id else ''
            record.ruc = store_id.ruc if store_id else ''
            record.fiscal_address = store_id.address if store_id else '' 
            
    @api.onchange('claimant_id')
    def onchange_claimant_id(self):
        for record in self:
            claimant_id = record.claimant_id
            record.claimant_department_id = claimant_id.state_id.id if claimant_id else False
            record.claimant_address = claimant_id.contact_address if claimant_id else ''
            record.claimant_identification_document = claimant_id.vat if claimant_id else ''
            record.claimant_phone = claimant_id.phone if claimant_id else ''
            record.claimant_cell_phone = claimant_id.mobile if claimant_id else ''
            record.claimant_email = claimant_id.email if claimant_id else ''
            
    @api.onchange('parent_ct_id')
    def onchange_parent_ct_id(self):
        for record in self:
            parent_ct_id = record.parent_ct_id
            record.parent_ct_identification_document = parent_ct_id.vat if parent_ct_id else ''
            record.parent_ct_address = parent_ct_id.contact_address if parent_ct_id else ''
            record.parent_ct_phone = parent_ct_id.phone if parent_ct_id else ''
            record.parent_ct_email = parent_ct_id.email if parent_ct_id else ''
            