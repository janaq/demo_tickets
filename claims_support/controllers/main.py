from odoo import http,_,fields
from odoo.http import request
from odoo.exceptions import UserError
import functools
import pytz
from datetime import datetime, timedelta, time

MONTHS = {
    '1': 'ENE',
    '2': 'FEB',
    '3': 'MAR',
    '4': 'ABR',
    '5': 'MAY',
    '6': 'JUN',
    '7': 'JUL',
    '8': 'AGO',
    '9': 'SET',
    '10': 'OCT',
    '11': 'NOV',
    '12': 'DIC'
}


def validationParameters(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        brand = kwargs.get('brand',False)
        shop = kwargs.get('shop',False)
        rangStart = kwargs.get('rangeStart',False)
        rangEnd = kwargs.get('rangEnd',False)
        tmp = kwargs.get('tmp',False)
        if not brand:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la marca."))
        if not shop:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la tienda."))
        if not rangStart:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para el rango de inicio."))
        if not rangEnd:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para el rango de finalización."))
        if not tmp:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la segmentación de datos."))
    return wrap
    
class ControllerDashboardNPS(http.Controller):
    
    
    def sectionResponseQueryGeneral(self,response):
        fields,values = ['S/N'],[0]
        if response:
            fields,values = [],[]
            for item in response:
                if item[1] > 0:
                    fields.append("NPS: {}".format(str(item[0])))
                    values.append(item[1])
        return fields,values
    
    def sectionResponseQuery(self,response,tmp):
        fields,values = ['S/N'],[0]
        if response:
            fields,values = [],[]
            for item in response:
                aux = 'S/N'
                if tmp == '1':
                    aux = item[0].strftime('%d-%m-%Y')    
                elif tmp == '2':
                    aux = 'S{}'.format(str(int(item[0])))
                elif tmp == '3':
                    aux = MONTHS.get(str(int(item[0])),'S/N')
                else:
                    aux = str(int(item[0]))
                fields.append(aux)
                values.append(item[1])
        return fields, values
        
    @http.route('/data_dashboardNPS', type='json', auth="public")
    def infoDashboardNPS(self,**kwargs):
        user_tz = request.env.user.tz or pytz.utc
        brand = kwargs.get('brand',False)
        shop = kwargs.get('shop',False)
        rangStart = kwargs.get('rangeStart',False)
        rangEnd = kwargs.get('rangEnd',False)
        tmp = kwargs.get('tmp',False)
        if not brand:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la marca."))
        if not shop:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la tienda."))
        if not rangStart:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para el rango de inicio."))
        if not rangEnd:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para el rango de finalización."))
        if not tmp:
            raise UserError(_("Información incompleta: Falta asignar valor de búsqueda para la segmentación de datos."))
        
        # Convertir rango de fechas a datetime (UTC) para la búsqueda en Odoo
        rangStart= fields.Date.from_string(rangStart) # Pasar de (str) a formato datetime
        rangStart = datetime.combine(rangStart,time.min) # Datetime con valor de 00:00:00
        rangStart = pytz.timezone(user_tz).localize(rangStart).astimezone(pytz.utc) # Datetime de zona horaria a UTC
        rangStart = rangStart.strftime('%Y-%m-%d %H:%M:%S')
        rangEnd= fields.Date.from_string(rangEnd) # Pasar de (str) a formato datetime
        rangEnd = datetime.combine(rangEnd,time.max) # Datetime con valor de 23:59:59
        rangEnd = pytz.timezone(user_tz).localize(rangEnd).astimezone(pytz.utc) # Datetime de zona horaria a UTC
        rangEnd = rangEnd.strftime('%Y-%m-%d %H:%M:%S')
        
        # DIFERENCIACIÓN POR SEGMENTACIÓN DE TIEMPO
        
        if tmp == '1':
            differentiation_tmp = """(rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date""".format(time_zone = user_tz)
        elif tmp == '2':
            differentiation_tmp = """EXTRACT ('week' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
        elif tmp == '3':
            differentiation_tmp = """EXTRACT ('month' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
        else:
            differentiation_tmp = """EXTRACT ('year' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
            
        # DIFERENCIACIÓN POR TIENDAS
        
        shops = '= {shop}'.format(shop=shop)
        if shop == 0:
            config_id = request.env['claim.config'].sudo().search([('id','=',brand)],limit=1)
            if config_id:
                shop = config_id.store_ids.ids if config_id.store_ids else []
                shops = 'in {shop}'.format(shop=shop)
        
        
        # NPS VALUE
        _sqlValue = """
            WITH NPS_VALUE AS (
                SELECT
                    rs.nps_value ,
                    COUNT(*) AS survey_values
                FROM response_survey rs
                INNER JOIN claim_config cc on cc.id = rs.config_id
                INNER JOIN helpdesk_tienda ht on ht.id = rs.store_id
                WHERE rs.nps_value BETWEEN 1 AND 10 AND cc.id = {brand} AND ht.id {shops} AND rs.date BETWEEN '{rangStart}' AND '{rangEnd}'
                GROUP BY rs.nps_value 
            ),
            surveys AS (
                SELECT SUM(survey_values) AS total FROM NPS_VALUE
            )
            SELECT
                r.response,
                --COALESCE(n.survey_values, 0) AS survey_values,
                (CAST(COALESCE(n.survey_values, 0) AS DECIMAL) / NULLIF(s.total, 0) * 100)
            FROM (
                SELECT generate_series(1, 10) AS response
            ) AS r
            LEFT JOIN NPS_VALUE n ON r.response = n.nps_value
            CROSS JOIN surveys s
            ORDER BY r.response;
        """.format(brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlValue)
        valueSurvey = request.env.cr.fetchall()
        fieldsValue, valuesValue = self.sectionResponseQueryGeneral(valueSurvey)
        
        # PARTICIPACIÓN EN LAS ENCUESTAS
        
        _sqlParticipation = """
            SELECT 
	            {differentiation_tmp},
	            count(*)
            FROM response_survey rs
            INNER JOIN claim_config cc on cc.id = rs.config_id
            INNER JOIN helpdesk_tienda ht on ht.id = rs.store_id
            WHERE cc.id = {brand} AND ht.id {shops} AND rs.date BETWEEN '{rangStart}' AND '{rangEnd}'
            GROUP BY {differentiation_tmp}
            ORDER BY {differentiation_tmp}
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlParticipation)
        participationSurvey = request.env.cr.fetchall()
        fieldsParticipation, valuesParticipation = self.sectionResponseQuery(participationSurvey,tmp)
        
        # NPS SCORE NETO = % PROMOTORES - % DETRACTORES
        
        _sqlScoreNeto = """
            WITH SCORE_NETO AS (
                SELECT
                    COUNT(*) FILTER (WHERE rs.response_survey = 'promoter') AS promoters,
                    COUNT(*) FILTER (WHERE rs.response_survey = 'detractor') AS detractors,
                    COUNT(*) AS surveys,
                    {differentiation_tmp} AS differentiation_tmp
                FROM response_survey rs 
                INNER JOIN claim_config cc on cc.id = rs.config_id
                INNER JOIN helpdesk_tienda ht on ht.id = rs.store_id
                WHERE cc.id = {brand} AND ht.id {shops} AND rs.date BETWEEN '{rangStart}' AND '{rangEnd}'
                GROUP BY {differentiation_tmp}
                ORDER BY {differentiation_tmp}
            )
            SELECT
                differentiation_tmp,
                ---promotores,
                ---detractores,
                ---total_encuestas,
                ---(CAST(promotores AS DECIMAL) / total_encuestas * 100) AS porcentaje_promotores,
                ---(CAST(detractores AS DECIMAL) / total_encuestas * 100) AS porcentaje_detractores,
                (CAST(promoters AS DECIMAL) / surveys * 100) - (CAST(detractors AS DECIMAL) / surveys * 100) AS nps_score
            FROM SCORE_NETO;
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlScoreNeto)
        scoreNetoSurvey = request.env.cr.fetchall()
        fieldsScoreNeto, valuesScoreNeto = self.sectionResponseQuery(scoreNetoSurvey,tmp)
        
        # NPS BREAKDOWN
        
        _sqlBreakdown = """"""
        #request.env.cr.execute(_sqlBreakdown)
        #breakdownSurvey = request.env.cr.fetchall()
        #fieldsBreakdown, valuesBreakdown = self.sectionResponseQuery(breakdownSurvey,tmp)
        
        
        
        
        
        
        
        return {
            'participationSurvey': {
                'fields': fieldsParticipation,
                'values': valuesParticipation
            },
            'netPromoterScore' :{
                'fields': fieldsScoreNeto,
                'values': valuesScoreNeto
            },
            'valueSurvey' :{
                'fields': fieldsValue,
                'values': valuesValue
            },
            
            
        }