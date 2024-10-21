from odoo import fields,models,api,_
from lxml import etree


class ImLivechatChannel(models.Model):
    
    _inherit = 'im_livechat.channel'
    
    allowed_operator_ids = fields.Many2many('res.users', 'imlivechat_channel_im_allowed_user', 'channel_id', 'user_id', string='Operadores permitidos')
    field_readonly = fields.Boolean(string='Solo lectura')
    
    @api.model
    def action_server_im_livechat_channel(self):
        #self.ensure_one()
        edit = self.env.user.has_group('im_livechat.im_livechat_group_manager')
        for record in self.env['im_livechat.channel'].search([]):
            record.field_readonly = not edit
        action = {
            'name': _('Canales de chat en vivo del sitio web'),
            'view_mode': 'kanban,form', 
            'res_model': 'im_livechat.channel',
            'type': 'ir.actions.act_window',
            'context': {"edit":edit,"field_readonly":not edit},
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    {}
                </p><p>
                    {} <span class="fa fa-long-arrow-right"/></p>
                """.format(_('Define un nuevo canal de chat en vivo del sitio web'),
                           _('Puedes crear canales para cada sitio web en el que quieras integrar el widget de chat en vivo del sitio web, lo que permitirá a los visitantes de tu sitio web hablar en tiempo real con tus operadores.')),
        }
        return action     