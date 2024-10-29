from odoo import models, api, fields


class MailMessage(models.Model):
    
    _inherit = 'mail.message'
    
    is_livechat_closing_message = fields.Boolean(string='Mensaje de cierre de chat en vivo',help='Identificador de mensajes de cierre de sesión del chat en vivo de forma manual por un operador')