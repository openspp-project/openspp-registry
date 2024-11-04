# Copyright 2018, XOE Solutions
# Copyright 2018-2019 Rafis Bikbov <https://it-projects.info/team/bikbov>
# Copyright 2019 Yan Chirino <https://xoe.solutions/>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=redefined-builtin

"""Pinguin module for Odoo REST Api.

This module implements plumbing code to the REST interface interface concerning
authentication, validation, ORM access and error codes.

It also implements a ORP API worker in the future (maybe).

Todo:
    * Implement API worker
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""
import base64
import functools
import logging
import traceback

import werkzeug.wrappers

import odoo
from odoo.http import request
from odoo.http import route as http_route
from odoo.service import security
from odoo.tools import date_utils
from odoo.tools.safe_eval import safe_eval

# fmt: off
from odoo.addons.spp_base_api.lib.pinguin import error_response, get_dict_from_record, get_model_for_read
from odoo.addons.spp_oauth.tools.rsa_encode_decode import OpenSPPOAuthJWTException, verify_and_decode_signature

# fmt: on
from odoo.addons.web.controllers.main import ReportController

try:
    import simplejson as json
except ImportError:
    import json


_logger = logging.getLogger(__name__)

####################################
# Definition of global error codes #
####################################

# 2xx Success
CODE__success = 200
CODE__created = 201
CODE__accepted = 202
CODE__ok_no_content = 204
# 4xx Client Errors
CODE__server_rejects = (400, "Server rejected", "Welcome to macondo!")
CODE__no_user_auth = (401, "Authentication", "Your token could not be authenticated.")
CODE__user_no_perm = (403, "Permissions", "%s")
CODE__method_blocked = (
    403,
    "Blocked Method",
    "This method is not whitelisted on this model.",
)
CODE__auth_method_not_supported = (
    403,
    "Authorization Method Not Supported",
    "The request authorization method is not supported by server!",
)
CODE__db_not_found = (404, "Db not found", "Welcome to macondo!")
CODE__canned_ctx_not_found = (
    404,
    "Canned context not found",
    "The requested canned context is not configured on this model",
)
CODE__obj_not_found = (
    404,
    "Object not found",
    "This object is not available on this instance.",
)
CODE__res_not_found = (404, "Resource not found", "There is no resource with this id.")
CODE__act_not_executed = (
    409,
    "Action not executed",
    "The requested action was not executed.",
)
# 5xx Server errors
CODE__invalid_method = (501, "Invalid Method", "This method is not implemented.")
CODE__invalid_spec = (
    501,
    "Invalid Field Spec",
    "The field spec supplied is not valid.",
)
# If API Workers are enforced, but non is available (switched off)
CODE__no_api_worker = (
    503,
    "API worker sleeping",
    "The API worker is currently not at work.",
)


def successful_response(status, data=None):
    """Successful responses wrapper.

    :param int status: The success code.
    :param data: (optional). The data that can be converted to a JSON.

    :returns: The werkzeug `response object`_.
    :rtype: werkzeug.wrappers.Response

    .. _response object:
        http://werkzeug.pocoo.org/docs/0.14/wrappers/#module-werkzeug.wrappers

    """
    try:
        response = json.dumps(data.ids)
    except AttributeError:
        response = json.dumps(data, default=date_utils.json_default) if data else None

    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=response,
    )


##########################
# Pinguin Authentication #
##########################


# User token auth (db-scoped)
def authenticate_token_for_user(token):
    """Authenticate against the database and setup user session corresponding to the token.

    :param str token: The raw access token.

    :returns: User if token is authorized for the requested user.
    :rtype odoo.models.Model

    :raise: werkzeug.exceptions.HTTPException if user not found.
    """
    _logger.info("authenticate_token_for_user: %s", token)
    user = request.env["res.users"].sudo().search([("openapi_token", "=", token)])
    if user.exists():
        # copy-pasted from odoo.http.py:OpenERPSession.authenticate()
        request.session.uid = user.id
        request.session.login = user.login
        request.session.session_token = user.id and security.compute_session_token(request.session, request.env)
        request.update_env(user=user.id)

        return user
    raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__no_user_auth))


def get_auth_header(headers, raise_exception=False):
    """check and get basic / bearer authentication header from headers

    :param werkzeug.datastructures.Headers headers: All headers in request.
    :param bool raise_exception: raise exception.

    :returns: Found raw authentication header.
    :rtype: str or None

    :raise: werkzeug.exceptions.HTTPException if raise_exception is **True**
                                              and auth header is not in headers
                                              or it is not Basic type.
    """
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not any([auth_header.startswith("Basic "), auth_header.startswith("Bearer ")]):
        if raise_exception:
            raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__no_user_auth))
    return auth_header


def get_data_from_auth_header(header):
    if header.startswith("Basic "):
        return get_data_from_basic_auth_header(header)
    if header.startswith("Bearer "):
        return get_data_from_bearer_auth_header(header)
    raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__auth_method_not_supported))


def get_data_from_basic_auth_header(header):
    """decode basic auth header and get data

    :param str header: The raw auth header.

    :returns: a tuple of database name and user token
    :rtype: tuple
    :raise: werkzeug.exceptions.HTTPException if basic header is invalid base64
                                              string or if the basic header is
                                              in the wrong format
    """
    normalized_token = header.replace("Basic ", "").replace("\\n", "").encode("utf-8")
    try:
        decoded_token_parts = base64.b64decode(normalized_token).decode("utf-8").split(":")
    except TypeError as e:
        raise werkzeug.exceptions.HTTPException(
            response=error_response(500, "Invalid header", "Basic auth header must be valid base64 string")
        ) from e

    if len(decoded_token_parts) == 1:
        db_name, user_token = None, decoded_token_parts[0]
    elif len(decoded_token_parts) == 2:
        db_name, user_token = decoded_token_parts
    else:
        err_descrip = (
            'Basic auth header payload must be of the form "<{}>" (encoded to base64)'.format("user_token")
            if odoo.tools.config["dbfilter"]
            else "db_name:user_token"
        )
        raise werkzeug.exceptions.HTTPException(response=error_response(500, "Invalid header", err_descrip))

    return db_name, user_token


def get_data_from_bearer_auth_header(header):
    """decode bearer auth header and get data

    :param str header: The raw auth header.

    :returns: a tuple of database name and user token
    :rtype: tuple
    :raise: werkzeug.exceptions.HTTPException if bearer header is invalid or if the bearer header is
                                              in the wrong format
    """
    normalized_token = header.replace("Bearer ", "").replace("\\n", "").encode("utf-8")

    try:
        res = verify_and_decode_signature(normalized_token)
    except OpenSPPOAuthJWTException as e:
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__no_user_auth)) from e

    if not all([key in res.keys() for key in ("database", "token")]):
        err_descrip = 'Bearer auth header payload must include "database" & "token"'
        raise werkzeug.exceptions.HTTPException(response=error_response(500, "Invalid header", err_descrip))
    return res["database"], res["token"]


def setup_db(request, db_name):
    """check and setup db in session by db name

    :param httprequest: a wrapped werkzeug Request object
    :type httprequest: :class:`werkzeug.wrappers.BaseRequest`
    :param str db_name: Database name.

    :raise: werkzeug.exceptions.HTTPException if the database not found.
    """
    if request.session.db:
        return
    if db_name not in odoo.service.db.list_dbs(force=True):
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__db_not_found))

    request.session.db = db_name


###################
# Pinguin Routing #
###################


def get_openapi_path(namespace, version, model, method_name):
    """Get the OpenAPI path for a given namespace, version and method.

    :param str namespace: The namespace name.
    :param str version: The version name.
    :param str method_name: The method name.

    :returns: The opensapi.path object.
    :rtype: path
    """
    _logger.info("get_openapi_path: %s %s %s %s", namespace, version, model, method_name)
    if not namespace or not version:
        raise werkzeug.exceptions.HTTPException(
            response=error_response(404, "Not Found", "Namespace and version are required")
        )

    http_method = request.httprequest.method.lower()
    # if api_method:
    #     http_method = "patch"

    # TODO: Handle custom functions

    domain_path = [
        ("namespace_id.name", "=", namespace),
        ("namespace_id.version_name", "=", version),
        ("name", "=", model),
        ("method", "=", http_method),
    ]
    _logger.info("get_openapi_path: %s", domain_path)
    path = request.env["spp_api.path"].sudo().search(domain_path, limit=1)

    _logger.info("get_openapi_path: %s", path)
    if not path:
        raise werkzeug.exceptions.HTTPException(
            response=error_response(
                404,
                "Not Found",
                "The requested URL was not found on the server. If you entered the "
                "URL manually please check your spelling and try again.",
            )
        )

    return path


# Try to get namespace from user allowed namespaces
def get_namespace_by_name_from_users_namespaces(user, namespace_name, raise_exception=False):
    """check and get namespace from users namespaces by name

    :param ..models.res_users.ResUsers user: The user record.
    :param str namespace_name: The name of namespace.
    :param bool raise_exception: raise exception if namespace does not exist.

    :returns: Found 'openapi.namespace' record.
    :rtype: ..models.openapi_namespace.Namespace

    :raise: werkzeug.exceptions.HTTPException if the namespace is not contained
                                              in allowed user namespaces.
    """
    namespace = request.env["spp_api.namespace"].search([("name", "=", namespace_name)])

    if not namespace.exists() and raise_exception:
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__obj_not_found))

    if namespace not in user.namespace_ids and raise_exception:
        err = list(CODE__user_no_perm)
        err[2] = "The requested namespace (integration) is not authorized."
        raise werkzeug.exceptions.HTTPException(response=error_response(*err))

    return namespace


# Create openapi.log record
def create_log_record(**kwargs):
    test_mode = request.registry.test_cr
    # don't create log in test mode as it's impossible in case of error in sql
    # request (we cannot use second cursor and we cannot use aborted
    # transaction)
    if not test_mode:
        with odoo.registry(request.session.db).cursor() as cr:
            # use new to save data even in case of an error in the old cursor
            env = odoo.api.Environment(cr, request.session.uid, {})
            _create_log_record(env, **kwargs)


def _create_log_record(
    env,
    namespace_id=None,
    namespace_log_request=None,
    namespace_log_response=None,
    user_id=None,
    user_request=None,
    user_response=None,
):
    """create log for request

    :param int namespace_id: Requested namespace id.
    :param string namespace_log_request: Request save option.
    :param string namespace_log_response: Response save option.
    :param int user_id: User id which requests.
    :param user_request: a wrapped werkzeug Request object from user.
    :type user_request: :class:`werkzeug.wrappers.BaseRequest`
    :param user_response: a wrapped werkzeug Response object to user.
    :type user_response: :class:`werkzeug.wrappers.Response`

    :returns: New 'openapi.log' record.
    :rtype: ..models.openapi_log.Log
    """
    if True:  # just to keep original indent
        log_data = {
            "namespace_id": namespace_id,
            "request": "%s | %s | %d" % (user_request.url, user_request.method, user_response.status_code),
            "request_data": None,
            "response_data": None,
        }
        if namespace_log_request == "debug":
            log_data["request_data"] = user_request.__dict__
        elif namespace_log_request == "info":
            log_data["request_data"] = user_request.__dict__
            for k in ["form", "files"]:
                try:
                    del log_data["request_data"][k]
                except KeyError:
                    _logger.debug("Key %s not found in request_data" % k)

        if namespace_log_response == "debug":
            log_data["response_data"] = user_response.__dict__
        elif namespace_log_response == "error" and user_response.status_code > 400:
            log_data["response_data"] = user_response.__dict__

        return env["spp_api.log"].create(log_data)


# Patched http route
def route(*args, **kwargs):
    """Set up the environment for route handlers.

    Patches the framework and additionally authenticates
    the API token and infers database through a different mechanism.

    :param list args: Positional arguments. Transparent pass through to the patched method.
    :param dict kwargs: Keyword arguments. Transparent pass through to the patched method.

    :returns: wrapped method
    """

    def decorator(controller_method):
        @http_route(*args, **kwargs)
        @functools.wraps(controller_method)
        def controller_method_wrapper(*iargs, **ikwargs):
            auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

            _logger.info("auth_header: %s", auth_header)
            _logger.info("iargs: %s", iargs)
            _logger.info("ikwargs: %s", ikwargs)

            namespace = ikwargs.get("namespace")
            version = ikwargs.get("version")
            model = ikwargs.get("model")
            method = ikwargs.get("method")

            db_name, user_token = get_data_from_auth_header(auth_header)
            _logger.info(f"db_name: {db_name} - user_token: {user_token}")
            setup_db(request, db_name)
            authenticated_user = authenticate_token_for_user(user_token)
            path = get_openapi_path(namespace, version, model, method)

            data_for_log = {
                "namespace": namespace,
                "version": version,
                "method": method,
                "path_id": path.id,
                "namespace_log_request": path.namespace_id.log_request,
                "namespace_log_response": path.namespace_id.log_response,
                "user_id": authenticated_user.id,
                "user_request": None,
                "user_response": None,
            }

            # Eval query parameters
            for k, v in ikwargs.items():
                try:
                    ikwargs[k] = safe_eval(v)
                except Exception:
                    # ignore errors
                    continue

            ikwargs["path"] = path

            try:
                response = controller_method(*iargs, **ikwargs)
            except werkzeug.exceptions.HTTPException as e:
                response = e.response
            except Exception as e:
                traceback.print_exc()
                if hasattr(e, "error") and isinstance(e.error, Exception):
                    e = e.error
                response = error_response(
                    status=500,
                    error=type(e).__name__,
                    error_description=e.name if hasattr(e, "name") else str(e),
                )

            data_for_log.update({"user_request": request.httprequest, "user_response": response})
            # create_log_record(**data_for_log)

            return response

        return controller_method_wrapper

    return decorator


############################
# Pinguin Metadata Helpers #
############################


# TODO: cache per model and database
# Get the specific context(openapi.access)
def get_create_context(namespace, model, canned_context):
    """Get the requested preconfigured context of the model specification.

    The canned context is used to preconfigure default values or context flags.
    That are used in a repetitive way in namespace for specific model.

    As this should, for performance reasons, not repeatedly result in calls to the persistence
    layer, this method is cached in memory.

    :param str namespace: The namespace to also validate against.
    :param str model: The model, for which we retrieve the configuration.
    :param str canned_context: The preconfigured context, which we request.

    :returns: A dictionary containing the requested context.
    :rtype: dict
    :raise: werkzeug.exceptions.HTTPException TODO: add description in which case
    """
    cr, uid = request.cr, request.session.uid

    # Singleton by construction (_sql_constraints)
    openapi_access = request.env(cr, uid)["openapi.access"].search(
        [("model_id", "=", model), ("namespace_id.name", "=", namespace)]
    )

    assert len(openapi_access) == 1, "'openapi_access' is not a singleton, bad construction."
    # Singleton by construction (_sql_constraints)
    context = openapi_access.create_context_ids.filtered(lambda r: r["name"] == canned_context)
    assert len(context) == 1, "'context' is not a singleton, bad construction."

    if not context:
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__canned_ctx_not_found))

    return context


# TODO: cache per model and database
# Get model configuration (openapi.access)
def get_model_openapi_access(namespace, version, model):
    """Get the model configuration and validate the requested namespace against the session.

    The namespace is a lightweight ACL + default implementation to integrate
    with various integration consumer, such as webstore, provisioning platform, etc.

    We validate the namespace at this latter stage, because it forms part of the http route.
    The token has been related to a namespace already previously

    This is a double purpose method.

    As this should, for performance reasons, not repeatedly result in calls to the persistence
    layer, this method is cached in memory.

    :param str namespace: The namespace to also validate against.
    :param str model: The model, for which we retrieve the configuration.

    :returns: The error response object if namespace validation failed.
        A dictionary containing the model API configuration for this namespace.
            The layout of the dict is as follows:
            ```python
            {'context':                 (Dict)      odoo context (default values through context),
            'out_fields_read_multi':    (Tuple)     field spec,
            'out_fields_read_one':      (Tuple)     field spec,
            'out_fields_create_one':    (Tuple)     field spec,
            'method' : {
                'public' : {
                     'mode':            (String)    one of 'all', 'none', 'custom',
                     'whitelist':       (List)      of method strings,
                 },
                'private' : {
                     'mode':            (String)    one of 'none', 'custom',
                     'whitelist':       (List)      of method strings,
                 },
                'main' : {
                     'mode':            (String)    one of 'none', 'custom',
                     'whitelist':       (List)      of method strings,
                 },
            }
            ```
    :rtype: dict
    :raise: werkzeug.exceptions.HTTPException if the namespace has no accesses.
    """
    # TODO: this method has code duplicates with openapi specification code (e.g. get_OAS_definitions_part)
    cr, uid = request.cr, request.session.uid
    # Singleton by construction (_sql_constraints)
    openapi_access = (
        request.env(cr, uid)["openapi.access"]
        .sudo()
        .search(
            [
                ("model_id", "=", model),
                ("namespace_id.name", "=", namespace),
                ("version_name", "=", version),
            ]
        )
    )
    if not openapi_access.exists():
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__canned_ctx_not_found))

    res = {
        "context": {},  # Take ot here FIXME: make sure it is for create_context
        "out_fields_read_multi": (),
        "out_fields_read_one": (),
        "out_fields_create_one": (),  # FIXME: for what?
        "method": {
            "public": {"mode": "", "whitelist": []},
            "private": {"mode": "", "whitelist": []},
            "main": {"mode": "", "whitelist": []},
        },
    }
    # Infer public method mode
    if openapi_access.api_public_methods and openapi_access.public_methods:
        res["method"]["public"]["mode"] = "custom"
        res["method"]["public"]["whitelist"] = openapi_access.public_methods.split()
    elif openapi_access.api_public_methods:
        res["method"]["public"]["mode"] = "all"
    else:
        res["method"]["public"]["mode"] = "none"

    # Infer private method mode
    if openapi_access.private_methods:
        res["method"]["private"]["mode"] = "custom"
        res["method"]["private"]["whitelist"] = openapi_access.private_methods.split()
    else:
        res["method"]["private"]["mode"] = "none"

    for c in openapi_access.create_context_ids.mapped("context"):
        res["context"].update(json.loads(c))

    res["out_fields_read_multi"] = openapi_access.read_many_id.export_fields.mapped("name") or ("id",)
    res["out_fields_read_one"] = openapi_access.read_one_id.export_fields.mapped("name") or ("id",)

    if openapi_access.public_methods:
        res["method"]["public"]["whitelist"] = openapi_access.public_methods.split()
    if openapi_access.private_methods:
        res["method"]["private"]["whitelist"] = openapi_access.private_methods.split()

    main_methods = ["api_create", "api_read", "api_update", "api_delete"]
    for method in main_methods:
        if openapi_access[method]:
            res["method"]["main"]["whitelist"].append(method)

    if len(res["method"]["main"]["whitelist"]) == len(main_methods):
        res["method"]["main"]["mode"] = "all"
    elif not res["method"]["main"]["whitelist"]:
        res["method"]["main"]["mode"] = "none"
    else:
        res["method"]["main"]["mode"] = "custom"

    return res


##################
# Pinguin Worker #
##################


def wrap__resource__get_report(namespace, report_external_id, docids, converter, success_code):
    """Return html or pdf report response.

    :param namespace: id/ids/browserecord of the records to print (if not used, pass an empty list)
    :param docids: id/ids/browserecord of the records to print (if not used, pass an empty list)
    :param docids: id/ids/browserecord of the records to print (if not used, pass an empty list)
    :param report_name: Name of the template to generate an action for
    """
    report = request.env.ref(report_external_id)

    if isinstance(report, type(request.env["ir.ui.view"])):
        report = request.env["report"]._get_report_from_name(report_external_id)

    model = report.model
    report_name = report.report_name

    get_model_openapi_access(namespace, model)

    response = ReportController().report_routes(report_name, docids, converter)
    response.status_code = success_code
    return response


#######################
# Pinguin ORM Wrapper #
#######################


# Dict from model
def get_dict_from_model(model, spec, id, **kwargs):
    """Fetch dictionary from one record according to spec.

    :param str model: The model against which to validate.
    :param tuple spec: The spec to validate.
    :param int id: The id of the record.
    :param dict kwargs: Keyword arguments.
    :param tuple kwargs['include_fields']: The extra fields.
        This parameter is not implemented on higher level code in order
        to serve as a soft ACL implementation on top of the framework's
        own ACL.
    :param tuple kwargs['exclude_fields']: The excluded fields.

    :returns: The python dictionary of the requested values.
    :rtype: dict
    :raise: werkzeug.exceptions.HTTPException if the record does not exist.
    """
    include_fields = kwargs.get("include_fields", ())  # Not actually implemented on higher level (ACL!)
    exclude_fields = kwargs.get("exclude_fields", ())

    model_obj = get_model_for_read(model)

    record = model_obj.browse([id])
    if not record.exists():
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__res_not_found))
    return get_dict_from_record(record, spec, include_fields, exclude_fields)
