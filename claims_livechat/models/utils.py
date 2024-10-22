import base64
import re

url_pattern = r'^/im_livechat/support/\d+/[A-Za-z0-9+/]+={0,2}/[A-Za-z0-9+/]+={0,2}$'
vals_pattern = r'([^/]+)/([^/]+)$'

def encode_parameter(param):
    param = str(param)
    return base64.urlsafe_b64encode(param.encode('utf-8')).decode('utf-8')
    
def decode_parameter(encoded_param):
    return base64.urlsafe_b64decode(encoded_param.encode('utf-8')).decode('utf-8')

def get_context(request,kwargs,channel):
    data = False
    model = kwargs.get('model',False)
    record = kwargs.get('record_id',False)
    if model and record:
        model = decode_parameter(model)
        record = decode_parameter(record)
        if type(record) == str:
            record = int(record)
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
    return data

def evaluate_livechat_url(string):
    parameters = False
    if re.match(url_pattern, string):
        match = re.search(vals_pattern, string) 
        if match: 
            first_value = match.group(1)
            second_value = match.group(2)
            parameters = {
                'model': first_value,
                'record_id': second_value
            }
    return parameters