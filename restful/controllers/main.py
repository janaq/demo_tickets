"""Part of odoo. See LICENSE file for full copyright and licensing details."""

from datetime import datetime
import functools
import logging
import traceback
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import (
    valid_response,
    invalid_response,
    extract_arguments,
    extract_fields,
    restful_ensure_db,
)
from odoo.addons.web.controllers.utils import ensure_db
import json
import re

_logger = logging.getLogger(__name__)


fields_type_to_eval = ["boolean"]

def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        restful_ensure_db()
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response(
                "access_token_not_found", "missing access token in request header", 401
            )
        access_token_data = (
            request.env["api.access_token"]
            .sudo()
            .search([("token", "=", access_token)], order="id DESC", limit=1)
        )
        _logger.info("ACCESS TOKEN INGRESADO: "+str(access_token))
        if (
            access_token_data.find_one_or_create_token(
                user_id=access_token_data.user_id.id
            )
            != access_token
        ):
            return invalid_response(
                "access_token", "token seems to have expired or invalid", 401
            )

        request.session.uid = access_token_data.user_id.id
        request.update_env(user=access_token_data.user_id)#.id
        return func(self, *args, **kwargs)

    return wrap


_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>"
           ]


#TODO make a feature to configure this
jnq_available_models = [
    "res.partner",
    "res.country",
    "res.state",
    "res.city"
]

class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["GET"], csrf=False)
    def get(self, model=None, id=None, **payload):
        """
            Return a record with the specific id

            domain: List -- An expression to filter wich records to return. Syntax [["field","= != ? ...",value]]
            limit: Integer -- Maximum number of records to return
            fields: List -- List containing the records fields to return. Syntax ["name","last_name","age", ...]
            offset: Integer -- Number of records to ignore, useful for pagination if needed
        
        
            la url-encoded data queda para clasificacion y mas importante, seleccion de base de datos a utilizar
            la data en json, se utiliza para realizar la parametrizacion y bùsqueda
        """
        restful_ensure_db()
        ioc_name = model
        json_parameters = request.httprequest.data
        model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if model:
            try:
                if not json_parameters:
                    json_parameters = payload.get("query","")
                domain, fields, offset, limit, order, context = extract_arguments(json_parameters)
                if id:
                    domain = [("id", "=", int(id))]
                recordset = request.env[model.model].sudo().with_context(context).search(
                        domain,
                        offset=offset,
                        limit=limit,
                        order=order,
                    )
                if fields == False or len(fields) == 0:
                    fields = recordset._fields.keys()
                return_data = []
                for record in recordset:
                    return_data.append( self.get_record_data_function(record,fields,model.model))
                #if data:
                self.jnq_create_audit_data("GET",ioc_name,str(recordset.ids),payload,return_data,200,request)
                return valid_response(return_data)
            except Exception as e:
                _logger.info(traceback.format_exc())
                # or
                #_logger.info(sys.exc_info()[2])
                request.env.cr.rollback()
                user_name = request.env.user.partner_id.name
                e = getattr(e, 'name', e)
                self.jnq_create_audit_data("GET",ioc_name,"",str(payload) + " ------- "+str(json_parameters),str(e),401,request,user_name)
                return invalid_response("params", e)
            #else:
            #    return valid_response(data)
        message = "The model %s is not available in the registry." % ioc_name
        self.jnq_create_audit_data("GET",ioc_name,"",payload,message,401,request)
        return invalid_response(
            "invalid object model",
            message,
        )

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["POST","OPTIONS"], csrf=False)
    def post(self, model=None, id=None, **payload):
        """Create a new record.
        Basic sage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 105,
            'child_ids': [
                {
                    'name': 'Contact',
                    'type': 'contact'
                },
                {
                    'name': 'Invoice',
                   'type': 'invoice'
                }
            ],
            'category_id': [{'id': 9}, {'id': 10}]
        }
        req = requests.post('%s/api/res.partner/' %
                            base_url, headers=headers, data=data)

        """
        # Manejo de la solicitud CORS para la respuesta
        response = http.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'  # Permitir solicitudes de cualquier origen
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # Métodos permitidos
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Token'  # Encabezados permitidos
        # Manejo de la solicitud OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return response  # Retornar solo los encabezados CORS en respuesta a OPTIONS
        
        restful_ensure_db()
        user_name = request.env.user.partner_id.name
        ioc_name = model
        model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if model:
            try:
                _logger.info(f"payload {payload}")
                record_data = json.loads(payload["query"])
                _logger.info(record_data)

                _logger.info(f"record_data {record_data}")
                self.process_references(record_data)
                resource = request.env[model.model].sudo().with_context(skip_api=True).create(record_data)
            except Exception as e:
                _logger.info(traceback.format_exc())
                # or
                #_logger.info(sys.exc_info()[2])
                request.env.cr.rollback()
                user_name = request.env.user.partner_id.name
                e = getattr(e, 'name', e)
                self.jnq_create_audit_data("POST",ioc_name,"",payload,str(e),400,request,user_name)
                return invalid_response("params", e,400)
            else:
                if "return_fields" in payload:
                    return_fields = extract_fields(payload.get('return_fields'))
                    data = [self.get_record_data_function(resource,return_fields,model.model)]
                else:
                    if hasattr(resource,'external_live_chat') and resource.external_live_chat:
                        data = {"id": resource.id,"external_live_chat":resource.external_live_chat,"message":'Operación exitosa'}
                    else:
                        data = {"id": resource.id,"message":'Operación exitosa'}
                
                self.jnq_create_audit_data("POST",ioc_name,str(resource.ids),payload,data,200,request,user_name)
                return valid_response(data)
        message = "The model %s is not available in the registry." % ioc_name
        self.jnq_create_audit_data("POST",ioc_name,"",payload,message,401,request,user_name)
        return invalid_response(
            "invalid object model",
            message,
            401
        )

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PUT"], csrf=False)
    def put(self, model=None, id=None, **payload):
        """Edit a given record using the incoming values"""
        restful_ensure_db()
        try:
            _id = int(id)
            if payload.get("query",False):
                new_payload = payload.get("query")
                new_payload = new_payload.replace("true","True")
                new_payload = new_payload.replace("false","False")
                payload = eval(new_payload)
        except Exception as e:
            message = "invalid literal %s for id with base " % id
            self.jnq_create_audit_data("PUT",str(model),"",payload,message + "\n" + str(e),401,request)
            return invalid_response(
                "invalid object id", "invalid literal %s for id with base " % id
            )
        _model = (
            request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        )
        if not _model:
            message = "The model %s is not available in the registry." % model
            self.jnq_create_audit_data("PUT",str(model),"",payload,message,404,request)
            return invalid_response(
                "invalid object model",
                message,
                404,
            )
        try:
            model_obj = request.env[_model.model].sudo().browse(_id)
            
            for field in payload:
                model_field = model_obj._fields.get(field,False)
                if model_field:
                    if model_field.type in fields_type_to_eval:
                        value = payload.get(field)
                        if type(value) == str:
                            value = value.replace("true","True")
                            value = value.replace("false","False")
                            payload.update({
                                field:eval(value)
                            })
            self.process_references(payload)
            
            model_obj.write(payload)
        except Exception as e:
            request.env.cr.rollback()
            #return invalid_response("exception", e.name)
            e = getattr(e, 'name', e)
            self.jnq_create_audit_data("PUT",str(model),"",payload,str(e),401,request)
            return invalid_response("exception", e)
        else:
            message = "update %s record with id %s successfully!" % (_model.model, _id)
            record_ids = model_obj.ids if model_obj != None or model_obj != False else []
            self.jnq_create_audit_data("PUT",str(model),str(record_ids),payload,message,200,request)
            return valid_response(
                message
            )

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["DELETE"], csrf=False)
    def delete(self, model=None, id=None, **payload):
        """Delete a record from database / do not mismatch it with an archive function"""
        restful_ensure_db()
        try:
            _id = int(id)
        except Exception as e:
            message="invalid object id", "invalid literal %s for id with base " % id
            self.jnq_create_audit_data("DELETE",str(model),[id],payload,message+"\n"+str(e),401,request)
            return invalid_response(
                message
            )
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            if record:
                record.unlink()
            else:
                return invalid_response(
                    "missing_record",
                    "record object with id %s could not be found" % _id,
                    404,
                )
        except Exception as e:
            request.env.cr.rollback()
            #return invalid_response("exception", e.name, 503)
            e = getattr(e, 'name', e)
            self.jnq_create_audit_data("DELETE",str(model),[id],payload,str(e),503,request)
            return invalid_response("exception", e, 503)
        else:
            message="record %s has been successfully deleted" % record.id
            self.jnq_create_audit_data("DELETE",str(model),[id],payload,message,200,request)
            return valid_response(message)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PATCH"], csrf=False)
    def patch(self, model=None, id=None, action=None, **payload):
        """Execute a given function on a record"""
        restful_ensure_db()
        try:
            _id = int(id)
        except Exception as e:
            message= "invalid literal %s for id with base " % id
            self.jnq_create_audit_data("PATCH",str(model),[id],payload,message,401,request,action=str(action))
            return invalid_response(
                "invalid object id", message
            )
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            _callable = action in [
                method for method in dir(record) if callable(getattr(record, method))
            ]
            if record and _callable:
                # action is a dynamic variable.
                result = getattr(record, action)(payload)
            else:
                message= "record object with id %s could not be found or %s object has no method %s"% (_id, model, action)
                self.jnq_create_audit_data("PATCH",str(model),[id],payload,message,404,request,action=str(action))
                return invalid_response(
                    "missing_record",
                    message,
                    404,
                )
        except Exception as e:
            request.env.cr.rollback()
            e = getattr(e, 'name', e)
            self.jnq_create_audit_data("PATCH",str(model),[id],payload,str(e),503,request,action=str(action))
            return invalid_response("exception", e, 503)
        else:
            if result:
                self.jnq_create_audit_data("PATCH",str(model),[id],payload,str(result),200,request,action=str(action))
                return valid_response(result)
            else:
                message = "record %s has been successfully patched" % record.id
                self.jnq_create_audit_data("PATCH",str(model),[id],payload,message,200,request,action=str(action))
                return valid_response(message)

    @http.route('/api/response.survey', type='http', auth='none', methods=['OPTIONS'])
    def options_response(self):
        response = http.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'  # o tu dominio específico
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Token'
        response.headers['Access-Control-Max-Age'] = '3600'  # Opcional: cuánto tiempo pueden ser cacheadas las credenciales
        return response

    def get_record_data_function(self,record,fields,model):
        record_dict = {}
        for field in fields:
            if (type(field) == list):
                curr_field=field[0]
                relational_fields = field[1]
            else:
                curr_field = field
                relational_fields = ["id","name"]
            field_type = request.env[model]._fields.get(curr_field,False)
            if field_type:
                field_type = field_type.type
            else:
                continue
            if (field_type=="many2one" or 
                field_type=="one2many" or
                field_type=="many2many"):
                if field_type=="many2one" and len(relational_fields) == 1 and relational_fields[0] in ["name","display_name"]:
                    record_dict.update({
                        curr_field: record[curr_field][relational_fields[0]]
                    })
                else:
                    relational_record = []
                    for rel_record in record[curr_field]:
                        relational_record.append(self.get_record_data_function(rel_record,relational_fields,rel_record._name))
                    record_dict.update({
                        curr_field: relational_record
                    })
            else:
                record_dict.update({
                    curr_field: str(record[curr_field])
                })
        return record_dict

    def process_references(self,record_data):
        ref_regex = r"^ref\(.+\..+\)$"
        if type(record_data) == dict:
            for data in record_data:
                if type(record_data[data]) == str:
                    if re.search(ref_regex, str(record_data[data])):
                        xml_id = str(record_data[data][4:-1])
                        record_data[data] = request.env.ref(xml_id).id
                elif type(record_data[data]) == list or type(record_data[data]) == dict:
                    self.process_references(record_data[data])
                else:
                    pass
        elif type(record_data) == list:
            index = -1
            for data in record_data:
                index += 1
                if type(record_data[index]) == str:
                    if re.search(ref_regex, str(record_data[index])):
                        xml_id = str(record_data[index][4:-1])
                        record_data[index] = request.env.ref(xml_id).id
                elif type(record_data[index]) == list or type(record_data[index]) == dict:
                    self.process_references(record_data[index])
                else:
                    pass

    def jnq_create_audit_data(self,method,model,records,payload,response,response_code,request,action=False,user_name = False):
        if user_name == False:
            user_name = request.env.user.partner_id.name
        audit_data= {
            "method":method,
            "related_model": model,
            "related_records": str(records),
            "related_action": str(action),
            "name": user_name+" -- "+ method +" -- " +str(model)+ "--" + str(datetime.now()),
            "payload":str(payload),
            "response_code":response_code,
            "response":str(response),
            "sid":request.session.sid,
            "remote_address":request.httprequest.environ.get("REMOTE_ADDR"),
        }
        request.env["restful.api_audit"].create(audit_data)