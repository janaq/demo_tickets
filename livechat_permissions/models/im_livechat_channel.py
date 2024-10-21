from odoo import fields,models,api,_
from lxml import etree


class ImLivechatChannel(models.Model):
    
    _inherit = 'im_livechat.channel'
    
    allowed_operator_ids = fields.Many2many('res.users', 'imlivechat_channel_im_allowed_user', 'channel_id', 'user_id', string='Operadores permitidos')