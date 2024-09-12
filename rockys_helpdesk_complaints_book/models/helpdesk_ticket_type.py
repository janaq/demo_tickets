from odoo import fields,models,api,_
import pytz
from datetime import datetime,timedelta,date

class HDTicketType(models.Model):
    
    _inherit = 'helpdesk.ticket.type'
    
    used_complaints_book = fields.Boolean(string='Libro de reclamaciones',help='Este campo indica si el tipo de ticket está habilitado para el libro de reclamaciones',default=False)