from odoo import models, api, fields


class MailMessage(models.Model):
    
    _inherit = 'mail.message'
    
    is_livechat_closing_message = fields.Boolean(string='Mensaje de cierre de chat en vivo',help='Identificador de mensajes de cierre de sesión del chat en vivo de forma manual por un operador')
    
    def _message_format(self, fnames, format_reply=True, legacy=False):
        vals = super(MailMessage,self)._message_format(fnames, format_reply=True, legacy=False)
        for val in vals:
            message = self.env['mail.message'].sudo().search([('id','=',val.get('id',0))],limit=1)
            if message:
                val['is_livechat_closing_message'] = message.is_livechat_closing_message
        return vals