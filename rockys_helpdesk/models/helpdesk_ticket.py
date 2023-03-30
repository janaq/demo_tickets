from odoo import fields,models,api,_

class HDTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    date_and_time = fields.Datetime('Fecha y hora')
    order_date_and_time = fields.Datetime('Fecha y hora de pedido')
    jor_id = fields.Many2one(comodel_name='helpdesk.jor', string='JOR')
    interaction_id = fields.Many2one(comodel_name='helpdesk.interaccion', string='Interacción')
    solution_id = fields.Many2one(comodel_name='helpdesk.soluciones', string='Solución')
    store_id = fields.Many2one(comodel_name='helpdesk.tienda', string='Tienda')
    call_reason = fields.Many2one(comodel_name='helpdesk.motivo_llamada', string='Motivo de llamada')
    supervisor_id = fields.Many2one(comodel_name='helpdesk.supervisor', string='Supervisor')
    partner_phone = fields.Char(string='Telefono', related="partner_id.phone",store=True,readonly=False)
    partner_mobile = fields.Char(string='Celular', related="partner_id.mobile",store=True,readonly=False)
    week_number = fields.Selection(string='N° de semana', selection=[
        ('0', 'SEMANA 1'),
        ('1', 'SEMANA 2'),
        ('2', 'SEMANA 3'),
        ('3', 'SEMANA 4'),
        ('4', 'SEMANA 5'),
        ('5', 'SEMANA 6')
    ])
