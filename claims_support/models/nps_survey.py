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
        
    def remove_availability(self):
        self.ensure_one()
        self.available = False
    
    
class AttentionSurvey(models.Model):
    
    _name = 'attention.survey'
    _description = 'Atención programada a los clientes'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'rating.mixin', 'mail.activity.mixin']
    
    name = fields.Char(string='Atención programada',tracking=True)
    partner_id = fields.Many2one('res.partner',string='Cliente',tracking=True)
    client_name = fields.Char(string='Nombre del cliente',tracking=True)
    client_email = fields.Char(string='Correo electrónico del cliente',tracking=True)
    phone = fields.Char(string='Teléfono del cliente',tracking=True)

    date = fields.Datetime(string='Fecha y hora',tracking=True)
    advisor_id = fields.Many2one('res.users',string='Asesor asignado',tracking=True)
    survey_id = fields.Many2one('response.survey',string='Encuesta NPS',domain="[('company_id','=',company_id)]")
    config_id = fields.Many2one('claim.config',string='Punto de gestión de reclamos',tracking=True)
    brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca',related='config_id.brand_id',tracking=True)
    allowed_store_ids = fields.Many2many('helpdesk.tienda',string='Tienda',compute='_compute_allowed_store_ids',store=True)
    store_id = fields.Many2one('helpdesk.tienda',string='Tienda',tracking=True,domain="[('id','in',allowed_store_ids)]")
    state = fields.Selection(selection=[('waiting', "En espera"),('attended', "Atendido"),('cancel',"Cancelado")],string='Estado',default='waiting',tracking=True)
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company)
    
    @api.depends('config_id')
    def _compute_allowed_store_ids(self):
        for record in self:
            shops = [] if not record.config_id else record.config_id.store_ids.ids
            record.allowed_store_ids = [(6,0,shops)]
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for record in self:
            partner_id = record.partner_id
            record.client_name = partner_id.name if partner_id else ''
            record.client_email = partner_id.email if partner_id else ''
            record.phone = partner_id.phone if partner_id else ''

    @api.onchange('survey_id')
    def onchange_survey_id(self):
        for record in self:
            survey_id = record.survey_id
            record.config_id = survey_id.config_id.id,
            record.store_id = survey_id.store_id.id,
            record.partner_id = survey_id.partner_id.id
            record.client_name = survey_id.client_name
            record.client_email = survey_id.client_email
            record.phone = survey_id.phone

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
    partner_id = fields.Many2one('res.partner',string='Cliente',tracking=True)
    client_name = fields.Char(string='Nombre del cliente',tracking=True)
    client_email = fields.Char(string='Correo electrónico del cliente',tracking=True)
    phone = fields.Char(string='Teléfono del cliente',tracking=True)
    
    nps_value = fields.Integer('Valor NPS',tracking=True)
    comment_ids = fields.Many2many('default.comment.survey',string='Comentarios',tracking=True)
    additional_comment = fields.Html('Comentario adicional',tracking=True)
    
    type_care = fields.Selection(selection=[('now', "Inmediata"),('scheduled', "Programada")],string='Tipo de atención',tracking=True)
    date = fields.Datetime(string='Fecha y hora del registro',default=_default_datetime_now,tracking=True)
    
    config_id = fields.Many2one('claim.config',string='Punto de gestión de reclamos',tracking=True)
    company_id = fields.Many2one('res.company',string='Compañía',default=lambda self: self.env.company,tracking=True)
    
    reward_ids = fields.One2many('reward.survey','survey_id',string='Recompensa',tracking=True)
    attention_ids = fields.One2many('attention.survey','survey_id',string='Programación',tracking=True)
    
    count_reward = fields.Integer('Recuento de recompensas',compute='_compute_count_reward',store=True)
    count_attention = fields.Integer('Recuento de atención',compute='_compute_count_attention',store=True,tracking=True)
    
    #store_id = fields.Many2one('helpdesk.tienda',string='Tienda',compute='_compute_information_config',store=True,tracking=True)
    brand_id = fields.Many2one('helpdesk.ticket.brand',string='Marca',compute='_compute_information_config',store=True,tracking=True)
    allowed_store_ids = fields.Many2many('helpdesk.tienda',string='Tienda',compute='_compute_allowed_store_ids',store=True)
    store_id = fields.Many2one('helpdesk.tienda',string='Tienda',tracking=True,domain="[('id','in',allowed_store_ids)]")
    requires_rewards = fields.Boolean(string='¿Requiere recompensa?',tracking=True,compute='_compute_information_config',store=True)
    created_service = fields.Boolean(string='¿Creado desde el servicio?',tracking=True)
    
    response_survey = fields.Selection([('detractor','Detractor'),('neutral','Neutro'),('promoter','Promotor'),('-','Sin asignar')],string='Clasificación de la respuesta',compute='_compute_response_survey',store=True)
    
    @api.depends('nps_value','config_id','config_id.range_detractors','config_id.range_neutrals','config_id.range_promoters')
    def _compute_response_survey(self):
        for record in self:
            config_id = record.config_id
            detractor = config_id.range_detractors.split(',') if config_id.range_detractors else []
            neutral = config_id.range_neutrals.split(',') if config_id.range_neutrals else []
            promoter = config_id.range_promoters.split(',') if config_id.range_promoters else []
            record.response_survey = '-'
            if str(record.nps_value) in detractor:
                record.response_survey = 'detractor'
            if str(record.nps_value) in neutral:
                record.response_survey = 'neutral'
            if str(record.nps_value) in promoter:
                record.response_survey = 'promoter'
        
    @api.depends('config_id')
    def _compute_allowed_store_ids(self):
        for record in self:
            shops = [] if not record.config_id else record.config_id.store_ids.ids
            record.allowed_store_ids = [(6,0,shops)]
            
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for record in self:
            partner_id = record.partner_id
            record.client_name = partner_id.name if partner_id else ''
            record.client_email = partner_id.email if partner_id else ''
            record.phone = (partner_id.mobile if partner_id.mobile else partner_id.phone) if partner_id else ''

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('skip_api',False):
            for val in vals_list:
                # La identificación del cliente se realiza a través del correo electrónico (dato obligatorio en cualquier parte de flujo y/o variantes)
                name = val.get('client_name','')
                email = val.get('client_email','')
                phone = val.get('phone','')
                partner_id = self.env['res.partner'].sudo().search([('email','=',email)],limit=1)
                # Si es que no se encuentra un contacto, se crea uno con los valores ingresados.
                # Aquí en el caso de tlf o móvil, solo puse la validación del número mayor o igual a 9.
                # Si no hay nombre, se le pone 'CLIENTE ANÓNIMO'
                if not partner_id:
                    partner_id = self.env['res.partner'].sudo().create({
                        'name': name if name != '' else 'CLIENTE ANÓNIMO',
                        'email': email,
                        'phone': phone if len(phone) < 9 else '',
                        'mobile': phone if len(phone) >= 9 else '',
                    })
                # Comprobando el nombre del ciente
                if partner_id and name == '':
                    val.update({
                        'client_name': partner_id.name
                    })
                # Para el registro de los comentarios predeterminados, debemos volver reemplazar los valores ingresados
                comments = eval(val.get('comment_ids','[]'))
                #items = []
                #for comment in comments:
                    #items.append(comment.id)
                    #rd = self.env.ref(comment)
                    #if rd:
                        #items.append(rd.id)
                # Para citas programadas. Se crea la programación en base a la fecha programada.
                attention = val.get('type_care',False)
                if attention == 'scheduled':
                    programming = {
                        'partner_id': partner_id.id,
                        'client_name': name if name != '' else 'CLIENTE ANÓNIMO',
                        'client_email': email,
                        'phone': phone,
                        'date': val.get('schedule_datetime',''),
                        'config_id': val.get('config_id',False),
                        'store_id': val.get('store_id',False),
                    }
                # Modificamos el val dentro de la lista de datos:
                # Agregamos el id del partner obtenido o creado
                val.update({
                    'partner_id': partner_id.id,
                    'comment_ids': [(6,0,comments)],
                    'created_service': True,
                })
                # Agregamos la programación:
                if attention == 'scheduled':
                    val.update({ 'attention_ids': [(0,0,programming)] })
                # Quitamos la fecha programada en caso exista:
                if 'schedule_datetime' in list(val.keys()):
                    del val['schedule_datetime']
        surveys = super(ResponseSurvey,self).create(vals_list)
        for survey in surveys:
            survey.name = self.env['ir.sequence'].next_by_code('survey.nps') or '/'
            if self._context.get('skip_api',False):
                survey.sending_reward_api()
        return surveys
    
    @api.depends('config_id','config_id.is_sending_rewards','config_id.brand_id')
    def _compute_information_config(self):
        for record in self:
            config_id = record.config_id
            record.brand_id = config_id.brand_id.id
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
    
    def send_customer(self):
        self.ensure_one()
        template_id = self.config_id.template_id if self.config_id.is_sending_rewards and (self.requires_rewards and self.config_id.template_id) else False
        template_id.send_mail(self.id)

    # Si el punto de gestión de reclamos requiere el envío de una recompensa 
    # y la encuesta no tiene una recompesa asignada
    def sending_reward(self):
        self.ensure_one()
        config_id = self.config_id
        if not self.client_email:
            raise UserError("¡Acción inconsistente! No se ingresó el correo electrónico del cliente para poder realizar el envío correspondiente de la recompensa.") 
        if config_id.is_sending_rewards and not config_id.template_id or self.requires_rewards and not config_id.template_id:
            raise UserError("¡Acción inconsistente! No se configuró la plantilla de correo electrónico para el envío de las recompensas al cliente.")
        if not config_id.is_sending_rewards or not self.requires_rewards:
            raise UserError("¡Acción inconsistente! No se configuró la el punto de gestión de reclamos para la realización de esta operación.")
        reward_id = self.env['reward.survey'].sudo().search([('available','=',True),('company_id','in',[False,self.company_id.id])],limit=1)
        if reward_id:
            # Envío con plantilla al correo del cliente y actualización de la información 
            reward_id.survey_id = self.id
            reward_id.remove_availability()
            self.send_customer()
        else:
            raise UserError("¡Acción inconsistente! Actualmente no se tiene recompensas disponibles para el envío al cliente y/o no se tiene configurada la opción de envío de recompensas al cliente.")
        
    def sending_reward_api(self):
        self.ensure_one()
        try:
            self.sending_reward()
        except UserError as e: 
            return {'warning': str(e)} 
        except Exception as e:  
            {'error': "Se produjo un error inesperado: " + str(e)}
    
    # Si la encuesta tiene atención programada
    # y no se tien una cita asociada
    def create_attention(self):
        self.ensure_one()
        self.env['attention.survey'].sudo().create({
            'partner_id': self.partner_id.id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'phone': self.phone,
            'survey_id': self.id,
            'company_id': self.company_id.id,
            'config_id': self.config_id.id,
            'store_id': self.store_id.id
        })