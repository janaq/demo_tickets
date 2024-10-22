"""Common methods"""
import ast
import logging
import werkzeug.wrappers
import json
from odoo.http import request
from datetime import datetime, date
from werkzeug.urls import iri_to_uri
from odoo import http

_logger = logging.getLogger(__name__)
try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ModuleNotFoundError as identifier:
    _logger.error(identifier)
else:
    import json


def valid_response(data, status=200,headers=None):
    """Valid Response
    This will be return when the http request was successfully processed."""
    for d in data:
        if type(d) == dict:
            for k, v in d.items():
                if type(v) is date:
                    d[k]=datetime.strftime(v, "%d/%m/%Y")
                if type(v) is datetime:
                    d[k]=datetime.strftime(v, "%d/%m/%Y %H:%M:%S")
                if type(v) is bytes:
                    d[k] = str(v)[2:-1]

    data = {"count": len(data), "data": data}
    return http.Response(json.dumps(data), status=200, headers=headers, mimetype='application/json')
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data),
    )


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {
                "type": typ,
                "message": str(message)
                if str(message)
                else "wrong arguments (missing validation)",
            }
        ),
    )
def extract_fields(payloads):
    fields = []
    data = str(payloads)
    try:
        payload = json.loads(data)
    except JSONDecodeError as e:
        _logger.error(e)
    finally:
        if payload.get("fields"):
            fields += payload.get("fields")
    
    return fields

def extract_arguments(payloads, offset=0, limit=0, order=None):
    """."""
    fields, domain, payload, context = [], [], {}, {}
    #data = str(payloads)
    if type(payloads) == str:
        payload = eval(payloads)
    else:
        payload = json.loads(payloads)
    if payload.get("domain"):
        for _domain in payload.get("domain"):
            if len(_domain)==3:
                l, o, r = _domain
                if o == "': '":
                    o = "="
                elif o == "!': '":
                    o = "!="
                domain.append(tuple([l, o, r]))
            elif len(_domain)==1:
                domain.append(_domain)
    if payload.get("fields"):
        fields += payload.get("fields")
    if payload.get("offset"):
        offset = int(payload["offset"])
    if payload.get("limit"):
        limit = int(payload.get("limit"))
    if payload.get("order"):
        order = payload.get("order")
    if payload.get("context"):
        context = payload.get("context")
    return [domain, fields, offset, limit, order,context]



def restful_ensure_db():
    db = request.params.get("db",False)
    if db and db not in http.db_filter([db]):
        db = None
    
    if not db:
        all_dbs = http.db_list(force=True)
        if len(all_dbs) == 1:
            db = all_dbs[0]

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            if r.data:
                json_string = str(json.loads(r.data))
                query_string = query_string + "&query="+json_string
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        werkzeug.exceptions.abort(request.redirect(url_redirect.to_url(), 302))


    if db != request.session.db:
        request.session = http.root.session_store.new()
        request.session.update(http.get_default_session(), db=db)
        request.session.context['lang'] = request.default_lang()
    #request.session.db = db
    #request.update_env(db=db)