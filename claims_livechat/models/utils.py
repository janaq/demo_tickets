import base64

def encode_parameter(param):
    param = str(param)
    return base64.urlsafe_b64encode(param.encode('utf-8')).decode('utf-8')
    
def decode_parameter(encoded_param):
    return base64.urlsafe_b64decode(encoded_param.encode('utf-8')).decode('utf-8')