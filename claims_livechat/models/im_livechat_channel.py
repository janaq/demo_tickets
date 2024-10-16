import base64
import random
import re

from odoo import api, Command, fields, models, modules, _


class ImLivechatChannel(models.Model):
    
    _inherit = 'im_livechat.channel'
    
    descriptive_message_required = fields.Boolean(string='Mensaje inicial descriptivo',default=False)
    
    def get_livechat_info(self, username=None,data=None):
        self.ensure_one()

        if username is None:
            username = _('Visitor')
        info = {}
        info['available'] = self.chatbot_script_count or len(self._get_available_users()) > 0
        info['server_url'] = self.get_base_url()
        if info['available']:
            info['options'] = self._get_channel_infos()
            info['options']['current_partner_id'] = self.env.user.partner_id.id
            info['options']["default_username"] = username
            if self.descriptive_message_required and data:
                info['options']['default_comment_username'] = """
                Hola! Mi nombre es {name} y recientemente he completado la encuesta {record},
                brindando un puntaje de {value}.
                """.format(name=username,record=data.name,value=data.nps_value)
        return info