from odoo import fields,models,api,_
from .utils import encode_parameter

class ResponseSurvey(models.Model):
    
    _inherit = 'response.survey'
    
    external_live_chat = fields.Char('LiveChat')
    channel_ids = fields.One2many('mail.channel','survey_id',string='Sesiones')
    count_channel = fields.Integer('Recuento de sesiones',compute='_compute_count_channel',store=True)
    
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
    
    @api.depends('channel_ids')
    def _compute_count_channel(self):
        for record in self:
            record.count_channel = len(record.channel_ids)
            
    def action_open_livechat(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.channel',
            'target': 'self',
            'context':{'create':False,'delete':False}
        }
        if len(self.channel_ids) == 1:
            action.update({
                'res_id': self.channel_ids.id,
                'view_id': self.env.ref('im_livechat.mail_channel_view_form').id,
                'view_mode': 'form',
            })
        if len(self.channel_ids) > 1:
            action.update({
                'name': 'Sesiones de livechat',
                'domain': [('id', 'in', self.channel_ids.mapped("id"))],
                'view_mode': 'tree',
                'view_id': self.env.ref('im_livechat.mail_channel_view_tree').id,
            })
        return action