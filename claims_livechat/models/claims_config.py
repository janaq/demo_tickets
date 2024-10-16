from odoo import fields,models,api,_

class ClaimsConfig(models.Model):
    
    _inherit = 'claim.config'
    
    live_claims_support = fields.Boolean('Soporte de reclamaciones en vivo')
    channel_id = fields.Many2one('im_livechat.channel',string='Canal')