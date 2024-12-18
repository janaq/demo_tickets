from odoo import http
from odoo.http import request
import base64
import io

from odoo.addons.web.controllers.binary import Binary

class MyBinary(Binary):
    
    @http.route('/public/image/<int:record_id>', type='http', auth='public', website=True)
    def public_image(self, record_id, **kwargs):
        record = request.env['helpdesk.tienda'].sudo().browse(record_id)
        if record.image:
            image_base64 = record.image
            return http.send_file(io.BytesIO(base64.b64decode(image_base64)), filename='logo.png', mimetype='image/png')
        return http.Response(status=404)