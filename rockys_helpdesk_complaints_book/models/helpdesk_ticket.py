from odoo import fields,models,api,_

class HDTicket(models.Model):
    
    _inherit = 'helpdesk.ticket'
    
    is_complaints_book = fields.Boolean(string='¿Es ticket del libro de reclamaciones?',compute='_compute_is_complaints_book',store=True)
    registration_date = fields.Date(string='Fecha de registro',default=fields.Datetime.today())
    date_and_time = fields.Datetime('Fecha y hora',default=fields.Datetime.now())
    # [1] ELECCIÓN DEL RESTAURANTE
    #restaurant_id = fields.Many2one('helpdesk.tienda',string='Restaurante')
    store_name = fields.Char(string='Nombre')
    business_name = fields.Char('Razón Social',tracking=True)
    ruc = fields.Char('RUC',tracking=True)
    fiscal_address = fields.Char('Dirección fiscal',tracking=True)
    brand_id = fields.Many2one('helpdesk.ticket.brand',tracking=True)
    # [2] IDENTIFICACIÓN DEL CONSUMIDOR RECLAMANTE
    claimant_id = fields.Many2one('res.partner',string='Reclamate',tracking=True)
    claimant_name = fields.Char('Nombre completo')
    claimant_department_id = fields.Many2one('res.country.state',string='Departamento',tracking=True)
    claimant_address = fields.Char('Dirección',tracking=True)
    claimant_identification_document = fields.Char('DNI/C.E.',tracking=True)
    claimant_phone = fields.Char('Teléfono',tracking=True)
    claimant_cell_phone = fields.Char('Celular',tracking=True)
    claimant_email = fields.Char('Correo electrónico',tracking=True)
    #Para el caso de menores de edad deberá registrarse adicionalmente el nombre del padre/madre
    parent_ct_id = fields.Many2one('res.partner',string='Padre/Madre',tracking=True)
    parent_ct_name = fields.Char('Nombre completo',tracking=True)
    parent_ct_identification_document = fields.Char('DNI',tracking=True)
    parent_ct_phone = fields.Char('Teléfono',tracking=True)
    parent_ct_address = fields.Char('Dirección',tracking=True)
    parent_ct_email = fields.Char('Correo electrónico',tracking=True)
    # [3] IDENTIFICACIÓN DEL PRODUCTO O SERVICIO CONTRATADO
    contracted_type = fields.Selection([('product','Producto'),('service','Servicio')],string='Tipo',tracking=True)
    order_number = fields.Char('Número del pedido',tracking=True)
    order_date = fields.Date('Fecha del pedido',tracking=True)
    order_channel_id = fields.Many2one('helpdesk.ticket.channel',string='Canal del pedido',tracking=True)
    reclaimed_amount = fields.Float('Monto reclamado',tracking=True)
    order_detail = fields.Html('Detalle del pedido',tracking=True)
    # [4] DETALLE RECLAMCIÓN Y PEDIDO DEL CONSUMIDOR
    type_claim = fields.Selection([('claim','Reclamo'),('complaint','Queja')],string='Tipo',tracking=True)
    claim_detail = fields.Html('Detalle del reclamo o queja',tracking=True)
    # [5] OBSERVACIONES Y ACCIONES ADOPTADAS POR EL PROVEEDOR
    action_date = fields.Date('Fecha',tracking=True)
    action_detail = fields.Html('Detalle',tracking=True)
    
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
    def _onchange_info_store_id(self):
        for record in self:
            store_id = record.store_id
            record.business_name = store_id.business_name if store_id else ''
            record.ruc = store_id.ruc if store_id else ''
            record.fiscal_address = store_id.address if store_id else ''
            record.store_name =  store_id.name if store_id else ''
            record.brand_id =  store_id.brand_id.id if store_id else False
            
    @api.onchange('claimant_id')
    def _onchange_info_claimant_id(self):
        for record in self:
            claimant_id = record.claimant_id
            record.claimant_department_id = claimant_id.state_id.id if claimant_id else False
            record.claimant_address = claimant_id.contact_address if claimant_id else ''
            record.claimant_identification_document = claimant_id.vat if claimant_id else ''
            record.claimant_phone = claimant_id.phone if claimant_id else ''
            record.claimant_cell_phone = claimant_id.mobile if claimant_id else ''
            record.claimant_email = claimant_id.email if claimant_id else ''
            record.claimant_name = claimant_id.name if claimant_id else ''
            
    @api.onchange('parent_ct_id')
    def _onchange_info_parent_ct_id(self):
        for record in self:
            parent_ct_id = record.parent_ct_id
            record.parent_ct_identification_document = parent_ct_id.vat if parent_ct_id else ''
            record.parent_ct_address = parent_ct_id.contact_address if parent_ct_id else ''
            record.parent_ct_phone = parent_ct_id.phone if parent_ct_id else ''
            record.parent_ct_email = parent_ct_id.email if parent_ct_id else ''
            record.parent_ct_name = parent_ct_id.name if parent_ct_id else ''
            
    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('skip_api',False):
            for val in vals_list:
                #[1] Cliente reclamante
                document_complaining = val.get('claimant_identification_document',False)
                if document_complaining:
                    complaining_id =  self.env['res.partner'].sudo().search([('vat','=',document_complaining)],limit=1)
                    if not complaining_id:
                        complaining_id = self.env['res.partner'].sudo().create({
                            'company_type': 'person' if len(document_complaining) < 11 else 'company',
                            'name': val.get('claimant_name',''),
                            'street': val.get('claimant_address',''),
                            'street2': '',
                            'city': '',
                            'state_id': val.get('claimant_department_id',False),
                            'zip': '',
                            'country_id': self.env.ref('base.pe').id,
                            'vat': document_complaining,
                            'phone': val.get('claimant_phone',''),
                            'mobile': val.get('claimant_cell_phone',''),
                            'email': val.get('claimant_email',''),
                            'type': 'contact'
                        })
                    val['claimant_id'] = complaining_id.id
                    val['partner_id'] = complaining_id.id
                #[2] Padre/Madre del reclamante (cuando es menor de edad)
                name_parent = val.get('parent_ct_name',False)
                document_parent = val.get('parent_ct_identification_document',False)
                phone_parent = val.get('parent_ct_phone',False)
                address_parent = val.get('parent_ct_address',False)
                email_parent = val.get('parent_ct_email',False)
                if name_parent or document_parent or phone_parent or address_parent or email_parent:
                    parent_id = self.env['res.partner']
                    if document_parent:
                        parent_id =  self.env['res.partner'].sudo().search([('vat','=',document_parent)],limit=1)
                    if not document_parent or not parent_id:
                        document_parent = document_parent if document_parent else '-'
                        parent_id = self.env['res.partner'].sudo().create({
                                'company_type': 'person' if len(document_parent) < 11 else 'company',
                                'name': val.get('parent_ct_name',''),
                                'street': val.get('parent_ct_address',''),
                                'street2': '',
                                'city': '',
                                'state_id': False,
                                'zip': '',
                                'country_id': self.env.ref('base.pe').id,
                                'vat': document_parent,
                                'phone': val.get('parent_ct_phone',''),
                                'mobile': '',
                                'email': val.get('parent_ct_email',''),
                                'type': 'contact'
                            })
                    val['parent_ct_id'] = parent_id.id
                #[3] Tienda/Restaurante
                document_store = val.get('ruc',False)
                name_store = val.get('store_name',False)
                if document_store and name_store:
                    store_id = self.env['helpdesk.tienda'].sudo().search([('ruc','=',document_store),('name','=',name_store)],limit=1)
                    if not store_id:
                        store_id = self.env['helpdesk.tienda'].sudo().create({
                            'name': val.get('store_name',''),
                            'business_name':  val.get('business_name',''),
                            'ruc': val.get('ruc',''),
                            'address' :val.get('fiscal_address','')
                        })
                    val['store_id'] = store_id.id
        tickets = super(HDTicket,self).create(vals_list)
        return tickets