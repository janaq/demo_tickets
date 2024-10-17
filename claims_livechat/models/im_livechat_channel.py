import base64
import random
import re

from odoo import api, Command, fields, models, modules, _

class MailChannel(models.Model):
    
    _inherit = 'mail.channel'
    
    survey_id = fields.Many2one('response.survey',string='Encuesta')

class ImLivechatChannel(models.Model):
    
    _inherit = 'im_livechat.channel'
    
    descriptive_message_required = fields.Boolean(string='Identificación del cliente',default=False,help='Permite enviar un mensaje por defecto al abrir el chat al operador con una identificación básica del cliente')
    
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
        if not user_id and ctx.get('partner',False):
            members_to_add.append(Command.create({'partner_id': ctx.get('partner')}))
        
        if chatbot_script:
            name = chatbot_script.title
        else:
            name = ' '.join([
                visitor_user.display_name if visitor_user else anonymous_name,
                ' , ',
                operator.livechat_username if operator.livechat_username else operator.name
            ])
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
            'survey_id': ctx.get('id',False) if ctx else False
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
        if ctx:
            msg_customer = ctx.get('msg_customer','¡Hola!')
        #if mail_channel and msg_customer:
        mail_channel.message_post( 
                                body=msg_customer, 
                                message_type="comment", 
                                subtype_xmlid="mail.mt_comment", # Tipo de mensaje (comentario) 
                                author_id=self.env.user.partner_id.id  # Autor del mensaje (usuario actual) 
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