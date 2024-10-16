
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    clm_live_claims_support = fields.Boolean('Soporte de reclamaciones en vivo',related='claim_config_id.live_claims_support', readonly=False)
    clm_channel_id = fields.Many2one('im_livechat.channel',string='Canal',related='claim_config_id.channel_id', readonly=False)