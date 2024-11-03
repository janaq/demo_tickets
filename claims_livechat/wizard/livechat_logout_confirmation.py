from odoo import fields,models,api,_

class LivechatLogoutConfirmationo(models.TransientModel):
    
    _name = 'livechat.logout.confirmation'
    _description = 'Confirmación del cierre del chat en vivo'
    
    channel_id = fields.Many2one('mail.channel')
    message = fields.Text(string="Mensaje",default=_('Al confirmar, el chat en vivo se cerrará automáticamente, poniendo fin a la asistencia brindada por el operador en tiempo real. Acto seguido se enviará una encuesta de satisfacción al cliente para valorar su experiencia.'))
    
    def continue_process(self):
        self.ensure_one()
        channel_id = self.channel_id
        if channel_id:
            channel_id.perform_manual_closing()