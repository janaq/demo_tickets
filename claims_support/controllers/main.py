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
    
    
    def sectionResponseQueryGeneral(self,response,validation):
        fields,values = ['S/N'],[0]
        if response:
            fields,values = [],[]
            for item in response:
                if validation:
                    if item[1] and item[1] > 0:
                        fields.append("NPS: {}".format(str(item[0])))
                        values.append(item[1])
                else:
                    fields.append(item[0])
                    values.append(item[1])
        if not fields and not values:
            fields,values = ['S/N'],[0]
        return fields,values
    
    def sectionResponseQuery(self,response,tmp,colum):
        if colum == 2:
            fields,values = ['S/N'],[0]
        if colum == 4:
            fields,valuesProm, valuesDetr, valuesNeut = ['S/N'],[0],[0],[0]
        if response:
            if colum == 2:
                fields,values = [],[]
            if colum == 4:
                fields,valuesProm, valuesDetr, valuesNeut = [],[],[],[]
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
                if colum == 2:
                    values.append(item[1])
                if colum == 4:
                    valuesProm.append(item[1])
                    valuesDetr.append(item[2])
                    valuesNeut.append(item[3])
        if colum == 2:
            return fields, values
        if colum == 4:
            return fields, valuesProm,valuesDetr,valuesNeut
        
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
        if shop == 0:
            config_id = request.env['claim.config'].sudo().search([('id','=',brand)],limit=1)
            shop = config_id.store_ids.ids if config_id.store_ids else [0,0]
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
            legend = False
        elif tmp == '2':
            legend = True
            differentiation_tmp = """EXTRACT ('week' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
        elif tmp == '3':
            legend = False
            differentiation_tmp = """EXTRACT ('month' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
        else:
            legend = False
            differentiation_tmp = """EXTRACT ('year' FROM (rs.date::timestamp at time zone 'UTC' at time zone '{time_zone}')::date)""".format(time_zone = user_tz)
            
        # DIFERENCIACIÓN POR TIENDAS
        
        shops = '= {shop}'.format(shop=shop) if type(shop) == int else 'in {shop}'.format(shop=str(shop).replace('[','(').replace(']',')'))
    
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
        fieldsValue, valuesValue = self.sectionResponseQueryGeneral(valueSurvey,True)
        
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
        fieldsParticipation, valuesParticipation = self.sectionResponseQuery(participationSurvey,tmp,2)
        
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
                ---promoters,
                ---detractors,
                ---surveys,
                ---(CAST(promoters AS DECIMAL) / surveys * 100) AS percentage_promoters,
                ---(CAST(detractors AS DECIMAL) / surveys * 100) AS percentage_detractors,
                (CAST(promoters AS DECIMAL) / surveys * 100) - (CAST(detractors AS DECIMAL) / surveys * 100) AS nps_score
            FROM SCORE_NETO;
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlScoreNeto)
        scoreNetoSurvey = request.env.cr.fetchall()
        fieldsScoreNeto, valuesScoreNeto = self.sectionResponseQuery(scoreNetoSurvey,tmp,2)
        
        # NPS BREAKDOWN
        
        _sqlBreakdown = """
            WITH BREAKDOWN AS (
                SELECT
                    COUNT(*) FILTER (WHERE rs.response_survey = 'promoter') AS promoters,
                    COUNT(*) FILTER (WHERE rs.response_survey = 'detractor') AS detractors,
                    COUNT(*) FILTER (WHERE rs.response_survey = 'neutral') AS neutrals,
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
                ---promoters,
                ---detractors,
                ---surveys,
                (CAST(promoters AS DECIMAL) / surveys * 100) AS percentage_promoters,
                (CAST(detractors AS DECIMAL) / surveys * 100) AS percentage_detractors,
                (CAST(neutrals AS DECIMAL) / surveys * 100) AS percentage_neutrals
                ---(CAST(promoters AS DECIMAL) / surveys * 100) - (CAST(detractors AS DECIMAL) / surveys * 100) AS nps_score
            FROM BREAKDOWN;
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlBreakdown)
        breakdownSurvey = request.env.cr.fetchall()
        fieldsBreakdown, valuesProm, valuesDetr, valuesNeut = self.sectionResponseQuery(breakdownSurvey,tmp,4)
        
        # NPS TIENDA (NPS SCORE NETO = % PROMOTORES - % DETRACTORES)
        _sqlParticipationShop = """
            SELECT 
	            ht.name,
	            count(*),
                ht.id
            FROM response_survey rs
            INNER JOIN claim_config cc on cc.id = rs.config_id
            INNER JOIN helpdesk_tienda ht on ht.id = rs.store_id
            WHERE cc.id = {brand}  AND rs.date BETWEEN '{rangStart}' AND '{rangEnd}'
            GROUP BY ht.id
            ORDER BY ht.id
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlParticipationShop)
        participationShop = request.env.cr.fetchall()
        fieldsParticipationShop, valuesParticipationShop = self.sectionResponseQueryGeneral(participationShop,False)
        
        _sqlScoreShop = """
            WITH SCORE_NETO AS (
                SELECT
                    COUNT(*) FILTER (WHERE rs.response_survey = 'promoter') AS promoters,
                    COUNT(*) FILTER (WHERE rs.response_survey = 'detractor') AS detractors,
                    COUNT(*) AS surveys,
                    ht.name AS shop,
                    ht.id
                FROM response_survey rs 
                INNER JOIN claim_config cc on cc.id = rs.config_id
                INNER JOIN helpdesk_tienda ht on ht.id = rs.store_id
                WHERE cc.id = {brand} AND rs.date BETWEEN '{rangStart}' AND '{rangEnd}'
                GROUP BY ht.id
                ORDER BY ht.id
            )
            SELECT
                shop,
                ---promoters,
                ---detractors,
                ---surveys,
                ---(CAST(promoters AS DECIMAL) / surveys * 100) AS percentage_promoters,
                ---(CAST(detractors AS DECIMAL) / surveys * 100) AS percentage_detractors,
                (CAST(promoters AS DECIMAL) / surveys * 100) - (CAST(detractors AS DECIMAL) / surveys * 100) AS nps_score
            FROM SCORE_NETO;
        """.format(differentiation_tmp=differentiation_tmp,brand=brand,shops=shops,rangStart=rangStart,rangEnd=rangEnd)
        request.env.cr.execute(_sqlScoreShop)
        scoreShop = request.env.cr.fetchall()
        fieldScoreShop, valueScoreShop = self.sectionResponseQueryGeneral(scoreShop,False)
        
        return {
            'general': {
                'legend': legend    
            },
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
            'breakdownSurvey':{
                'fields': fieldsBreakdown,
                'valuesProm': valuesProm,
                'valuesDetr': valuesDetr,
                'valuesNeut': valuesNeut
            },
            'shopSurvey': {
                'fieldsParticipation': fieldsParticipationShop,
                'valuesParticipation': valuesParticipationShop,
                'valuesPromoterSCore': valueScoreShop,
            }
        }