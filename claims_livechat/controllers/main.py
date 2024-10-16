from odoo import http, tools, _
from odoo.http import request
from odoo.http import Response

from odoo.addons.im_livechat.controllers.main import LivechatController


class MyLivechatController(LivechatController):
    
    @http.route(['/im_livechat/support/<int:channel_id>','/im_livechat/support/<int:channel_id>/<string:model>/<int:record_id>'], type='http', auth='public')
    def support_page(self, channel_id, **kwargs):
        channel = request.env['im_livechat.channel'].sudo().browse(channel_id)
        # Guardar datos en la sesión
        http.request.session['model'] = kwargs.get('model',False)
        http.request.session['record_id'] = kwargs.get('record_id',False)
        return http.request.render('im_livechat.support_page', {'channel': channel})

    @http.route(['/im_livechat/loader/<int:channel_id>','/im_livechat/loader/<int:channel_id>/<string:model>/<int:record_id>'], type='http', auth='public')
    def loader(self, channel_id, **kwargs):
        # Obtener información de la sesión
        model = http.request.session.get('model')
        record_id = http.request.session.get('record_id')
        data = request.env[model].sudo().search([('id','=',record_id)])
        username = kwargs.get("username", _("Visitor"))
        if data:
            username = data.client_name
        channel = request.env['im_livechat.channel'].sudo().browse(channel_id)
        info = channel.get_livechat_info(username=username,data=data)
        return request.render('im_livechat.loader', {'info': info}, headers=[('Content-Type', 'application/javascript')])