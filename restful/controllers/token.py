# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import invalid_response, valid_response,restful_ensure_db


_logger = logging.getLogger(__name__)

expires_in = "restful.access_token_expires_in"


class AccessToken(http.Controller):
    """."""

    @http.route(
        "/api/auth/token", methods=["GET","OPTIONS"], type="http", auth="none"
    )
    def token(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           eq = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))
        """
        # Establecer los encabezados CORS
        headers = {
            'Access-Control-Allow-Origin': '*',  # para permitir todos los orígenes
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Access-Token',
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache'
        }
        # Manejar la solicitud OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return http.Response(status=200, headers=headers)
        
        restful_ensure_db()
        self._expires_in = request.env.ref(expires_in).sudo().value
        _token = request.env["api.access_token"]
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing error",
                    "either of the following are missing [db, username,password]",
                    403,
                )
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid database:
            info = "connection error {}".format((e))
            error = "connection error"
            _logger.error(info)
            return invalid_response(error,info,404)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(error, info,401)

        # Generate tokens
        access_token = _token.find_one_or_create_token(user_id=uid, create=True)
        # Successful response:
        return http.Response(json.dumps({
                    "uid": uid,
                    #"user_context": request.session._Session__data.get("context") or {} if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "access_token": access_token,
                    "expires_in": self._expires_in,
                }), status=200, headers=headers, mimetype='application/json')
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*")],
            response=json.dumps(
                {
                    "uid": uid,
                    #"user_context": request.session._Session__data.get("context") or {} if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "access_token": access_token,
                    "expires_in": self._expires_in,
                }
            ),
        )

    @http.route(
        "/api/auth/token", methods=["DELETE","OPTIONS"], type="http", auth="none", csrf=False
    )
    def delete(self, **post):
        """."""
        headers = {
            'Access-Control-Allow-Origin': '*',  # para permitir todos los orígenes
            'Access-Control-Allow-Methods': "DELETE , OPTIONS",
            'Access-Control-Allow-Headers': 'Content-Type, Access-Token',
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache'
        }
        # Manejar la solicitud OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return http.Response(status=200, headers=headers)
        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("access_token")
        access_token = _token.search([("token", "=", access_token)])
        if not access_token:
            info = "No access token was provided in request!"
            error = "no_access_token"
            _logger.error(info)
            return invalid_response(error, info,400)
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response(
            data={"desc": "token successfully deleted", "delete": True},status=200,headers=headers
        )
