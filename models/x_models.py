from odoo import fields,models,api,_

class XSupervisor(models.Model):
    _name = 'helpdesk.supervisor'
    _description = 'Supervisor'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    phone = fields.Char(string='Telefono', related="partner_id.phone",store=True,readonly=False)
    mobile = fields.Char(string='Celular', related="partner_id.mobile",store=True,readonly=False)
    email = fields.Char(string='Correo electronico', related="partner_id.email",store=True,readonly=False)


class XMotivoLlamada(models.Model):
    _name = 'helpdesk.motivo_llamada'
    _description = 'Motivo de llamada'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    interaccion_id = fields.Many2one(comodel_name='helpdesk.interaccion', string='Interaccion')
    notes = fields.Text(string='Notas')
    sequence = fields.Integer(string='Secuencia')

class XTienda(models.Model):
    _name = 'helpdesk.tienda'
    _description = 'Tienda'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    address = fields.Char(string='Dirección')
    image = fields.Binary(string='Imagen')
    supervisor_id = fields.Many2one(comodel_name='helpdesk.supervisor', string='Supervisor')
    jor_id = fields.Many2one(comodel_name='helpdesk.jor', string='JOR')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    phone = fields.Char(string='Telefono', related="partner_id.phone",store=True,readonly=False)
    mobile = fields.Char(string='Celular', related="partner_id.mobile",store=True,readonly=False)
    email = fields.Char(string='Correo electronico', related="partner_id.email",store=True,readonly=False)
    notes = fields.Text(string='Notas')
    sequence = fields.Integer(string='Secuencia')
    store_type = fields.Selection(string='Tipo de tienda', selection=[('0', 'Cadena'),
                                                                      ('1', 'Franquicia'),])

class XSoluciones(models.Model):
    _name = 'helpdesk.soluciones'
    _description = 'Soluciones'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    interaccion_id = fields.Many2one(comodel_name='helpdesk.interaccion', string='Interaccion')
    notes = fields.Text(string='Notas')
    sequence = fields.Integer(string='Secuencia')

class XInteracciones(models.Model):
    _name = 'helpdesk.interaccion'
    _description = 'Interaccion'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    notes = fields.Text(string='Notas')
    sequence = fields.Integer(string='Secuencia')

class XJOR(models.Model):
    _name = 'helpdesk.jor'
    _description = 'JOR'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']

    active = fields.Boolean(string='Activo', default=True)
    name = fields.Char(string='Nombre')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    phone = fields.Char(string='Telefono', related="partner_id.phone",store=True,readonly=False)
    mobile = fields.Char(string='Celular', related="partner_id.mobile",store=True,readonly=False)
    email = fields.Char(string='Correo electronico', related="partner_id.email",store=True,readonly=False)
    notes = fields.Text(string='Notas')
    sequence = fields.Integer(string='Secuencia')
