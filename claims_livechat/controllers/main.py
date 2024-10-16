from odoo import http, tools, _
from odoo.http import request
from odoo.http import Response

from odoo.addons.im_livechat.controllers.main import LivechatController
from ..models.utils import decode_parameter


class MyLivechatController(LivechatController):
    
    @http.route(['/im_livechat/support/<int:channel_id>','/im_livechat/support/<int:channel_id>/<string:model>/<string:record_id>'], type='http', auth='public')
    def support_page(self, channel_id, **kwargs):
        channel = request.env['im_livechat.channel'].sudo().browse(channel_id)
        # Guardar datos en la sesión
        data = False
        model = kwargs.get('model',False)
        record = kwargs.get('record_id',False)
        if model and record:
            model = decode_parameter(model)
            record = decode_parameter(record)
            data = request.env[model].sudo().search([('id','=',record)])
            data = {
                'id': data.id,
                'name': data.name,
                'partner': data.partner_id.id,
                'customer': data.client_name,
                'nps': data.nps_value
            }
            if channel.descriptive_message_required and data:
                data.update({
                    'msg_customer': """¡Hola! Mi nombre es {name} y recientemente he completado la encuesta {record} brindando un puntaje de {value}.""".format(name=data.get('customer'),record=data.get('name','/'),value=data.get(str('nps'),'0'))
                })
        http.request.session['data'] = data
        return http.request.render('im_livechat.support_page', {'channel': channel})

    @http.route(['/im_livechat/loader/<int:channel_id>','/im_livechat/loader/<int:channel_id>/<string:model>/<string:record_id>'], type='http', auth='public')
    def loader(self, channel_id, **kwargs):
        # Obtener información de la sesión
        data = http.request.session.get('data',False)
        username = kwargs.get("username", _("Visitor"))
        if data:
            username = data.get('customer',_("Visitor"))
        channel = request.env['im_livechat.channel'].sudo().browse(channel_id)
        info = channel.get_livechat_info(username=username)
        return request.render('im_livechat.loader', {'info': info}, headers=[('Content-Type', 'application/javascript')])
    
    @http.route('/im_livechat/get_session', type="json", auth='public', cors="*")
    def get_session(self, channel_id, anonymous_name, previous_operator_id=None, chatbot_script_id=None, persisted=True, **kwargs):
        # Para obtener información
        data = http.request.session.get('data',False)
        #
        user_id = None
        country_id = None
        # if the user is identifiy (eg: portal user on the frontend), don't use the anonymous name. The user will be added to session.
        if request.session.uid:
            user_id = request.env.user.id
            country_id = request.env.user.country_id.id
        else:
            # if geoip, add the country name to the anonymous name
            if request.geoip:
                # get the country of the anonymous person, if any
                country_code = request.geoip.get('country_code', "")
                country = request.env['res.country'].sudo().search([('code', '=', country_code)], limit=1) if country_code else None
                if country:
                    country_id = country.id

        if previous_operator_id:
            previous_operator_id = int(previous_operator_id)

        chatbot_script = False
        if chatbot_script_id:
            frontend_lang = request.httprequest.cookies.get('frontend_lang', request.env.user.lang or 'en_US')
            chatbot_script = request.env['chatbot.script'].sudo().with_context(lang=frontend_lang).browse(chatbot_script_id)

        return request.env["im_livechat.channel"].with_context(lang=False,data=data).sudo().browse(channel_id)._open_livechat_mail_channel(
            anonymous_name,
            previous_operator_id=previous_operator_id,
            chatbot_script=chatbot_script,
            user_id=user_id,
            country_id=country_id,
            persisted=persisted
        )