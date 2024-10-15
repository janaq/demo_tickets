
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    def _default_claim_config(self):
        # Default to the last modified pos.config.
        active_model = self.env.context.get('active_model', '')
        if active_model == 'claim.config':
            return self.env.context.get('active_id')
        return self.env['claim.config'].search([('company_id', '=', self.env.company.id)], limit=1)
    
    claim_config_id = fields.Many2one('claim.config', string="Punto de gestión de reclamos",default=lambda self: self._default_claim_config())
    # [ Campos del modelo de gestión de reclamaciones ]
    clm_name = fields.Char(string='Gestión de Reclamaciones', related='claim_config_id.name', readonly=False, help='Una identificación interna de la gestión de reclamaciones.',compute='_compute_clm_name',store=True)
    clm_code = fields.Char(string='Código', related='claim_config_id.code', readonly=False)
    clm_screen_saver_image_1920 = fields.Image('Protector de pantalla', max_width=1920, max_height=1920, related='claim_config_id.screen_saver_image_1920', readonly=False)
    clm_title = fields.Char('Título', related='claim_config_id.title', readonly=False)
    clm_description = fields.Char('Descripción', related='claim_config_id.description', readonly=False)
    clm_logo_image_1920 = fields.Image('Logo',max_width=1920, max_height=1920, related='claim_config_id.logo_image_1920', readonly=False)
    clm_is_sending_rewards = fields.Boolean('Activar envío de recompensas', related='claim_config_id.is_sending_rewards', readonly=False)
    #clm_store_id = fields.Many2one('helpdesk.tienda',string='Tienda',related='claim_config_id.store_id', readonly=False)
    clm_brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca',related='claim_config_id.brand_id', readonly=False)
    clm_template_id = fields.Many2one('mail.template',string='Plantilla de correo',related='claim_config_id.template_id', readonly=False)
    
    def action_claim_config_create_new(self):
        return {
            'view_mode': 'form',
            'res_model': 'claim.config',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': False,
            'context': {'claim_config_open_modal': True, 'claim_config_create_mode': True},
        }
        
    @api.depends('clm_brand_id')
    def _compute_clm_name(self):
        for record in self:
            record.clm_name = '' if not record.clm_brand_id else record.clm_brand_id.name