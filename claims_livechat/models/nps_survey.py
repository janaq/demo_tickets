from odoo import fields,models,api,_
from .utils import encode_parameter

class ResponseSurvey(models.Model):
    
    _inherit = 'response.survey'
    
    external_live_chat = fields.Char('LiveChat')
    
    @api.model_create_multi
    def create(self, vals_list):
        surveys = super(ResponseSurvey,self).create(vals_list)
        for survey in surveys:
            if self._context.get('skip_api',False) and survey.type_care == 'now' \
                and survey.config_id.live_claims_support and survey.config_id.channel_id:
                    channel_id = survey.config_id.channel_id.web_page
                    model_name = encode_parameter(self.env['response.survey']._name)
                    record_id = encode_parameter(survey.id)
                    survey.external_live_chat = "{base}/{param1}/{param2}".format(base=channel_id,param1=model_name,param2=str(record_id))            
        return surveys