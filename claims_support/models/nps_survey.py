from odoo import fields,models,api,_
import pytz
from datetime import datetime,timedelta,date
from odoo.exceptions import ValidationError, UserError

class DefaultCommentSurvey(models.Model):
    
    _name = 'default.comment.survey'
    _description = 'Comentarios predeterminados de la encuesta'
    
    name = fields.Char(string='Nombre corto')
    description = fields.Char(string='Descripción')
    active = fields.Boolean(string='Activo',default=True)
    company_id = fields.Many2one('res.company', string='Compañía')
    
    
class RewardsSurvey(models.Model):
    
    _name = 'reward.survey'
    _description = 'Recompensas de la encuesta'
    
    code = fields.Char('Código')
    available = fields.Boolean('Disponible para envío',default=True)
    survey_id = fields.Many2one('response.survey',string='Encuesta NPS')
    company_id = fields.Many2one('res.company',string='Compañía')
    
    def send_customer(self):
        self.ensure_one()
        
    def remove_availability(self):
        self.ensure_one()
        self.available = False
    
    
class AttentionSurvey(models.Model):
    
    _name = 'attention.survey'
    _description = 'Atención programada a los clientes'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']
    
    name = fields.Char(string='Atención programada',tracking=True)
    client_name = fields.Char(string='Nombre del cliente',tracking=True)
    client_email = fields.Char(string='Correo electrónico del cliente',tracking=True)
    phone = fields.Char(string='Teléfono del cliente',tracking=True)

    date = fields.Datetime(string='Fecha y hora',tracking=True)
    advisor_id = fields.Many2one('res.users',string='Asesor asignado',tracking=True)
    survey_id = fields.Many2one('response.survey',string='Encuesta NPS',domain="[('company_id','=',company_id)]")
     
    state = fields.Selection(selection=[('waiting', "En espera"),('attended', "Atendido"),('cancel',"Cancelado")],string='Estado',default='waiting',tracking=True)
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        attentions = super(AttentionSurvey,self).create(vals_list)
        for attention in attentions:
            attention.name = self.env['ir.sequence'].next_by_code('customer.attention') or '/'
        return attentions
    
    def action_attending(self):
        for record in self:
            record.state = 'attended'
    
    def action_cancelling(self):
        for record in self:
            record.state = 'cancel'
            
    def action_waiting(self):
        for record in self:
            record.state = 'waiting'
    
    
class ResponseSurvey(models.Model):
    
    _name = 'response.survey'
    _description = 'Respuesta de la encuesta'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']
    
    
    def _default_datetime_now(self):
        return fields.Datetime.context_timestamp(self, datetime.now()).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    name = fields.Char('Encuesta',tracking=True)
    client_name = fields.Char(string='Nombre del cliente',tracking=True)
    client_email = fields.Char(string='Correo electrónico del cliente',tracking=True)
    phone = fields.Char(string='Teléfono del cliente',tracking=True)
    
    nps_value = fields.Integer('Valor NPS',tracking=True)
    comment_ids = fields.Many2many('default.comment.survey',string='Comentarios',tracking=True)
    additional_comment = fields.Html('Comentario adicional',tracking=True)
    
    type_care = fields.Selection(selection=[('now', "Inmediata"),('scheduled', "Programada")],string='Tipo de atención',default='now',tracking=True)
    date = fields.Datetime(string='Fecha y hora del registro',default=_default_datetime_now,tracking=True)
    
    config_id = fields.Many2one('claim.config',string='Punto de gestión de reclamos',tracking=True)
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company,tracking=True)
    
    reward_ids = fields.One2many('reward.survey','survey_id',string='Recompensa',tracking=True)
    attention_ids = fields.One2many('attention.survey','survey_id',string='Programación',tracking=True)
    
    count_reward = fields.Integer('Recuento de recompensas',compute='_compute_count_reward',store=True)
    count_attention = fields.Integer('Recuento de atención',compute='_compute_count_attention',store=True,tracking=True)
    
    store_id = fields.Many2one('helpdesk.tienda',string='Tienda',compute='_compute_information_config',store=True,tracking=True)
    requires_rewards = fields.Boolean(string='¿Requiere recompensa?',tracking=True,compute='_compute_information_config',store=True)
    created_service = fields.Boolean(string='¿Creado desde el servicio?',tracking=True)
    

    @api.model_create_multi
    def create(self, vals_list):
        surveys = super(ResponseSurvey,self).create(vals_list)
        for survey in surveys:
            survey.name = self.env['ir.sequence'].next_by_code('survey.nps') or '/'
        return surveys
    
    @api.depends('config_id','config_id.is_sending_rewards')
    def _compute_information_config(self):
        for record in self:
            config_id = record.config_id
            record.store_id = config_id.store_id.id
            record.requires_rewards = config_id.is_sending_rewards
            
    @api.depends('attention_ids')
    def _compute_count_attention(self):
        for record in self:
            record.count_attention = len(record.attention_ids)
            
    def action_open_customer_attention(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'attention.survey',
            'target': 'self',
            'context':{'create':False,'delete':False}
        }
        if len(self.attention_ids) == 1:
            action.update({
                'res_id': self.attention_ids.id,
                'view_ids': [(False, 'form')],
                'view_mode': 'form',
            })
        if len(self.attention_ids) > 1:
            action.update({
                'name': 'Atenciones programadas',
                'domain': [('id', 'in', self.attention_ids.mapped("id"))],
                'view_mode': 'tree,form',
            })
        return action
        
    @api.depends('reward_ids')
    def _compute_count_reward(self):
        for record in self:
            record.count_reward = len(record.reward_ids)
            
    def action_open_customer_reward(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'reward.survey',
            'target': 'self',
            'context':{'create':False,'delete':False,'edit':False},
            'view_mode': 'tree',
        }
        if len(self.reward_ids) > 0:
            action.update({
                'name': 'Recompensas enviadas',
                'domain': [('id', 'in', self.reward_ids.ids)],
            })
        return action
    
    # Si el punto de gestión de reclamos requiere el envío de una recompensa 
    # y la encuesta no tiene una recompesa asignada
    def sending_reward(self):
        self.ensure_one()
        reward_id = self.env['reward.survey'].sudo().search([('available','=',True),('company_id','in',[False,self.company_id.id])],limit=1)
        if reward_id and self.requires_rewards:
            if not self.client_email:
                raise UserError("¡Acción inconsistente! No se ingresó el correo electrónico del cliente para poder realizar el envío correspondiente de la recompensa.") 
            # Envío con plantilla al correo del cliente y actualización de la información 
            reward_id.send_customer()
            reward_id.survey_id = self.id
            reward_id.remove_availability()
        else:
            raise UserError("¡Acción inconsistente! Actualmente no se tiene recompensas disponibles para el envío al cliente y/o no se tiene configurada la opción de envío de recompensas al cliente.")
        
    # Si la encuesta tiene atención programada
    # y no se tien una cita asociada
    def create_attention(self):
        self.ensure_one()
        self.env['attention.survey'].sudo().create({
            'client_name': self.client_name,
            'client_email': self.client_email,
            'phone': self.phone,
            'survey_id': self.id,
            'company_id': self.company_id.id
        })