import base64
import random
import re

from odoo import api, Command, fields, models, modules, _

class MailChannel(models.Model):
    
    _inherit = 'mail.channel'
    
    survey_id = fields.Many2one('response.survey',string='Encuesta')
    survey_url = fields.Char(string="Encuesta(URL)")

    
    def channel_info(self):
        """ Extends the channel header by adding the livechat operator and the 'anonymous' profile
            :rtype : list(dict)
        """
        channel_infos = super().channel_info()
        channel_infos_dict = dict((c['id'], c) for c in channel_infos)
        for channel in self:
            channel_infos_dict[channel.id]['channel']['survey_url'] = channel.survey_url
            channel_infos_dict[channel.id]['channel']['survey_id'] = channel.survey_id.id
        return list(channel_infos_dict.values())
     
class ImLivechatChannel(models.Model):
    
    _inherit = 'im_livechat.channel'
    
    msg_background_operator = fields.Char(default="#dee1e9", help="Color de fondo predeterminado del mensaje de chat en vivo del operador")
    msg_background_public = fields.Char(default="#e1e9de", help="Color de fondo predeterminado del mensaje de chat en vivo del visitante")
    msg_text_color_operator = fields.Char(default="#0a0a0a", help="Color de texto predeterminado del mensaje de chat en vivo del operador")
    msg_text_color_public = fields.Char(default="#0a0a0a", help="Color de texto predeterminado del mensaje de chat en vivo del visitante")
    msg_border_color_operator = fields.Char(default="#8da3dd", help="Color del borde predeterminado del mensaje de chat en vivo del operador")
    msg_border_color_public = fields.Char(default="#97db7d", help="Color del borde predeterminado del mensaje de chat en vivo del visitante")
    msg_font_size = fields.Char(string='Tamaño de la fuente',help="Tamaño de la fuente en el chat en vivo",default='14px')
    msg_font_family = fields.Char(string='Familia de la fuente',help='Familia de la fuente en el chat en vivo',default='ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"')
    allow_manual_exit = fields.Boolean(string='Cierre manual',help='Habilita la salida manual desde el chat en vivo (x)',default=True)
    
    descriptive_message_required = fields.Boolean(string='Identificación del cliente',default=False,help='Permite enviar un mensaje por defecto al abrir el chat al operador con una identificación básica del cliente')
    automatically_deploy = fields.Boolean(string='Desplegar automáticamente',default=False,help='Permite desplagar la venta de chat de forma automática al momento de iniciar la sesión')
    
    title_standby_screen = fields.Char('Título',default='Estamos en busca de un operador disponible para atender tu solicitud y darte el mejor servicio posible.')
    subtitle_standby_screen = fields.Char('Subtítulo',default='¡Gracias por tu paciencia! Estaremos contigo en breve.')
    color_text_standby_screen = fields.Char(default="#008C36", help="Color de fondo predeterminado del mensaje de chat en vivo del operador")
    color_loader_standby_screen = fields.Char(default="#7fc59a", help="Color de fondo predeterminado del mensaje de chat en vivo del visitante")
    
    def get_livechat_info(self, username=None):
        vals = super().get_livechat_info()
        vals['identifier'] = self.id
        return vals
    
    def _get_channel_infos(self):
        vals = super()._get_channel_infos()
        vals['msg_background_operator'] = self.msg_background_operator
        vals['msg_background_public'] = self.msg_background_public
        vals['msg_text_color_operator'] = self.msg_text_color_operator
        vals['msg_text_color_public'] = self.msg_text_color_public
        vals['msg_border_color_operator'] = self.msg_border_color_operator
        vals['msg_border_color_public'] = self.msg_border_color_public
        vals['automatically_deploy'] = self.automatically_deploy
        vals ['msg_font_size'] = self.msg_font_size
        vals ['msg_font_family'] = self.msg_font_family
        vals['allow_manual_exit']= self.allow_manual_exit
        return vals
        
    def _get_livechat_mail_channel_vals(self, anonymous_name, operator=None, chatbot_script=None, user_id=None, country_id=None):
        # partner to add to the mail.channel
        operator_partner_id = operator.partner_id.id if operator else chatbot_script.operator_partner_id.id
        members_to_add = [Command.create({'partner_id': operator_partner_id, 'is_pinned': False})]
        visitor_user = False
        if user_id:
            visitor_user = self.env['res.users'].browse(user_id)
            if visitor_user and visitor_user.active and operator and visitor_user != operator:  # valid session user (not public)
                members_to_add.append(Command.create({'partner_id': visitor_user.partner_id.id}))
        
        # Obteniendo contexto para agregar al partner de la encuesta que es un usuario público de ser el caso
        ctx = self._context.get('data',{})
        #if not user_id and ctx.get('partner',False):
            #members_to_add.append(Command.create({'partner_id': ctx.get('partner')}))
        
        if chatbot_script:
            name = chatbot_script.title
        else:
            name = ' '.join([
                visitor_user.display_name if visitor_user else anonymous_name,
                ' , ',
                operator.livechat_username if operator.livechat_username else operator.name
            ])
        # Obteniendo información de la encuesta NPS
        survey_id = ctx.get('id',False) if ctx else False
        if survey_id:
            base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = "{base}/web#id={id}&model={model}&view_type=form".format(base=base,id=survey_id,model='response.survey')
        channel = {
            'channel_member_ids': members_to_add,
            'livechat_active': True,
            'livechat_operator_id': operator_partner_id,
            'livechat_channel_id': self.id,
            'chatbot_current_step_id': chatbot_script._get_welcome_steps()[-1].id if chatbot_script else False,
            'anonymous_name': False if user_id else anonymous_name,
            'country_id': country_id,
            'channel_type': 'livechat',
            'name': name,
            'survey_id': survey_id,
            'survey_url': url if survey_id else False
        }
        return channel

    def _open_livechat_mail_channel(self, anonymous_name, previous_operator_id=None, chatbot_script=None, user_id=None, country_id=None, persisted=True):
        """ Return a livechat session. If the session is persisted, creates a mail.channel record with a connected operator or with Odoobot as
            an operator if a chatbot has been configured, or return false otherwise
            :param anonymous_name : the name of the anonymous person of the session
            :param previous_operator_id : partner_id.id of the previous operator that this visitor had in the past
            :param chatbot_script : chatbot script if there is one configured
            :param user_id : the id of the logged in visitor, if any
            :param country_code : the country of the anonymous person of the session
            :param persisted: whether or not the session should be persisted
            :type anonymous_name : str
            :return : channel header
            :rtype : dict

            If this visitor already had an operator within the last 7 days (information stored with the 'im_livechat_previous_operator_pid' cookie),
            the system will first try to assign that operator if he's available (to improve user experience).
        """
        self.ensure_one()
        user_operator = False
        if chatbot_script:
            if chatbot_script.id not in self.env['im_livechat.channel.rule'].search(
                    [('channel_id', 'in', self.ids)]).mapped('chatbot_script_id').ids:
                return False
        elif previous_operator_id:
            available_users = self._get_available_users()
            # previous_operator_id is the partner_id of the previous operator, need to convert to user
            if previous_operator_id in available_users.mapped('partner_id').ids:
                user_operator = next(available_user for available_user in available_users if available_user.partner_id.id == previous_operator_id)
        if not user_operator and not chatbot_script:
            user_operator = self._get_random_operator()
        if not user_operator and not chatbot_script:
            # no one available
            return False
        mail_channel_vals = self._get_livechat_mail_channel_vals(anonymous_name, user_operator, chatbot_script, user_id=user_id, country_id=country_id)
        #if persisted:
            # create the session, and add the link with the given channel
        mail_channel = self.env["mail.channel"].with_context(mail_create_nosubscribe=False).sudo().create(mail_channel_vals)
        if user_operator:
            mail_channel._broadcast([user_operator.partner_id.id])
        # Obteniendo contexto para agregar al partner de la encuesta que es un usuario público de ser el caso
        ctx = self._context.get('data',False)
        msg_customer = ''
        email_from = ''
        if ctx:
            msg_customer = ctx.get('msg_customer','¡Hola!')
            email_from = ctx.get('customer','Anónimo')
        if mail_channel and msg_customer and email_from:
            mail_channel.message_post( 
                                    body=msg_customer, 
                                    message_type="comment", 
                                    subtype_xmlid="mail.mt_comment", # Tipo de mensaje (comentario),
                                    email_from= email_from, # Desde donde se mandó el mensaje
                                    author_id= False  # Autor del mensaje (usuario actual) 
            )
        return mail_channel.sudo().channel_info()[0]
        #else:
            #operator_partner_id = user_operator.partner_id if user_operator else chatbot_script.operator_partner_id
            #display_name = operator_partner_id.user_livechat_username or operator_partner_id.display_name
            #return {
                #'name': mail_channel_vals['name'],
                #'chatbot_current_step_id': mail_channel_vals['chatbot_current_step_id'],
                #'state': 'open',
                #'operator_pid': (operator_partner_id.id, display_name.replace(',', '')),
                #'chatbot_script_id': chatbot_script.id if chatbot_script else None,
            #}