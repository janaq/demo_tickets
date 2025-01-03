from odoo import fields,models,api,_,Command

class HelpdeskTeam(models.Model):
    
    _inherit = "helpdesk.team"
    
    
    carbon_message_partner_id = fields.Many2one('res.partner',string='Copia carbón de todos los tickets')
    
    def _default_stage_ids(self):
        default_stages = self.env['helpdesk.stage']
        for xml_id in ['stage_new', 'stage_in_progress', 'stage_solved', 'stage_cancelled']:
            stage = self.env.ref('helpdesk.%s' % xml_id, raise_if_not_found=False)
            if stage:
                default_stages += stage
        if not default_stages:
            default_stages = self.env['helpdesk.stage'].create({
                'name': _("New"),
                'sequence': 0,
                #'template_id': self.env.ref('helpdesk.new_ticket_request_email_template', raise_if_not_found=False).id or None
            })
        return [Command.set(default_stages.ids)]