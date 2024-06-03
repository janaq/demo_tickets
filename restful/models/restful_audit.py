from odoo import api, fields, models


class RestfulAPIAudit(models.Model):
    _name = 'restful.api_audit'
    _description = 'Auditoria de solicitudes API'
    _order = "create_date desc"

    name = fields.Char(string='Nombre')
    payload = fields.Text(string='Payload')
    response_code = fields.Char(string='Codigo de respuesta')
    response = fields.Text(string='Respuesta')

    related_model = fields.Char(string='Modelo relacionado')
    related_records = fields.Char(string='Id de registro relacionado')
    related_action = fields.Char(string='Función ejecutada en registros')

    state = fields.Selection([
        ('success', 'Exito'),
        ('failed', 'Fallido')
    ], string='Estado', compute="jnq_get_state",stored=True)

    method = fields.Selection(string='', selection=[
        ('GET', 'Obtener'),
        ('POST', 'Crear'),
        ('PUT', 'Editar'),
        ('DELETE', 'Eliminar'),
        ('PATCH', 'Ejecutar funcion de registro'),
    ])

    sid = fields.Char(string='Id de session API')
    remote_address = fields.Char(string='Direccion remota de llamada')

    @api.depends("response_code")
    def jnq_get_state(self):
        for record in self:
            if record.response_code == "200":
                record.state = "success"
            else:
                record.state = "failed"