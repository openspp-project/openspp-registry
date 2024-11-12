import json
import uuid
from datetime import datetime, timezone

import werkzeug.wrappers

from odoo.http import Controller, request, route
from odoo.osv.expression import AND
from odoo.service.db import list_dbs
from odoo.tools import date_utils

from odoo.addons.spp_oauth.tools import OpenSPPOAuthJWTException, verify_and_decode_signature

from ..tools import constants


def setup_db(req, db_name):
    """check and setup db in session by db name

    :param httprequest: a wrapped werkzeug Request object
    :type httprequest: :class:`werkzeug.wrappers.BaseRequest`
    :param str db_name: Database name.

    :raise: werkzeug.exceptions.HTTPException if the database not found.
    """

    if not db_name:
        return 400, {
            "error": "Bad Request",
            "error_description": "db_name is required.",
        }

    if db_name not in list_dbs(force=True):
        return 404, {"error": "Not Found", "error_description": "DB not found."}

    req.session.db = db_name
    return 200, None


def response_wrapper(status, data):
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=date_utils.json_default) if data else None,
    )


def error_wrapper(code, message):
    error = {"error": {"code": code, "message": message}}
    return response_wrapper(code, error)


def get_auth_header(headers, raise_exception=False):
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if raise_exception:
            error = {
                "error": "Unauthorized",
                "error_description": "Your token could not be authenticated.",
            }
            return response_wrapper(401, error)
    return auth_header


class SppDciApiServer(Controller):
    @route(
        constants.OAUTH2_ENDPOINT,
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def auth_get_access_token(self, **kw):
        req = request

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return response_wrapper(
                400,
                {
                    "error": "Bad Request",
                    "error_description": "data must be in JSON format.",
                },
            )

        client_id = data.get("client_id", "")
        client_secret = data.get("client_secret", "")
        grant_type = data.get("grant_type", "")
        db_name = data.get("db_name", "")

        status_code, error_message = setup_db(req, db_name)
        if error_message:
            return response_wrapper(status_code, error_message)

        # req = Request(req.httprequest)

        if not all([client_id, client_secret, grant_type]):
            error = {
                "error": "Bad Request",
                "error_description": "client_id, client_secret, and grant_type is required.",
            }
            return response_wrapper(400, error)

        client = (
            req.env["spp.dci.api.client.credential"]
            .sudo()
            .search(
                [("client_id", "=", client_id), ("client_secret", "=", client_secret)],
                limit=1,
            )
        )

        if not client:
            error = {
                "error": "Unauthorized",
                "error_description": "Invalid client id or secret.",
            }
            return response_wrapper(401, error)

        access_token = client.generate_access_token(db_name)

        data = {
            "access_token": access_token,
            "token_type": "Bearer",
        }
        return response_wrapper(200, data)

    @route(
        constants.SYNC_SEARCH_ENDPOINT,
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def retrieve_registry(self, page=1, limit=30, **kw):
        auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

        access_token = auth_header.replace("Bearer ", "").replace("\\n", "").encode("utf-8")

        try:
            payload = verify_and_decode_signature(access_token)
        except OpenSPPOAuthJWTException:
            return error_wrapper(401, "Invalid Access Token.")

        req = request
        db_name = payload.get("db_name")
        status_code, error_message = setup_db(req, db_name)
        if error_message:
            return error_wrapper(status_code, error_message["error_description"])
        # req = Request(req.httprequest)

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        header = data.get("header", "")

        header_error = self.check_content(
            header,
            "header",
            ["message_id", "message_ts", "action", "sender_id"],
        )
        if header_error:
            return error_wrapper(header_error.get("code"), header_error.get("message"))

        message = data.get("message", "")
        message_error = self.check_content(message, "message", ["transaction_id", "search_request"])
        if message_error:
            return error_wrapper(message_error.get("code"), message_error.get("message"))

        message_id = header["message_id"]
        transaction_id = message.get("transaction_id")
        search_requests = message["search_request"]

        today_isoformat = datetime.now(timezone.utc).isoformat()
        correlation_id = str(uuid.uuid4())

        page = int(page)
        limit = int(limit)

        # Process search requests and modify search_responses
        search_responses = []
        pagination = {
            "page": page,
            "limit": limit,
            "total_records": 0,
            "total_pages": 0,
        }
        self.process_search_requests(search_requests, today_isoformat, search_responses, pagination)

        header = {
            "message_id": message_id,
            "message_ts": today_isoformat,
            "action": "search",
            "status": "succ",
        }
        message = {
            "transaction_id": transaction_id,
            "correlation_id": correlation_id,
            "search_response": search_responses,
        }

        data = {
            "header": header,
            "message": message,
            "pagination": pagination,
        }
        return response_wrapper(200, data)

    def check_content(self, content, label, required_parameters):
        """
        The function checks if a content has all the required parameters and returns an error message if
        any parameter is missing.

        :param content: The `content` parameter is the data that needs to be checked for certain
        conditions. It could be a dictionary, a list, or any other data type that you want to validate
        :param label: The label parameter is a string that represents the name or label of the content
        being checked. It is used in the error messages to provide context for the missing or invalid
        parameters
        :param required_parameters: A list of parameters that are required in the content
        :return: a dictionary with a "code" and "message" key. The "code" key represents the status code
        of the response, and the "message" key provides a descriptive message about the error or
        requirement.
        """
        if not content:
            return {"code": 400, "message": f"{label} is required."}

        for param in required_parameters:
            if param not in content:
                parameter_str = ", ".join(required_parameters)
                return {
                    "code": 400,
                    "message": f"{label} should have these parameters: {parameter_str}",
                }

        return None

    def process_queries(self, query_type, queries, domain):
        """
        The function processes queries by checking their content and constructing a domain based on the
        query type and attributes.

        :param query_type: The `query_type` parameter is a string that specifies the type of query being
        processed. It is used to determine the logic for processing the queries
        :param queries: The `queries` parameter is a list of dictionaries. Each dictionary represents a
        query and contains information about the query, such as the expression to be evaluated
        :param domain: The "domain" parameter in the given code represents a domain expression that is
        used to filter data based on certain conditions. It is initially passed as an argument to the
        function and is updated based on the queries processed within the function
        :return: the updated domain after processing the queries.
        """
        for query in queries:
            if query_type == constants.PREDICATE:
                query_error = self.check_content(query, "query", ["expression1"])
                if query_error:
                    return error_wrapper(query_error.get("code"), query_error.get("message"))

                expression = query.get("expression1")
                expression_error = self.check_content(
                    expression,
                    "expression1",
                    ["attribute_name", "operator", "attribute_value"],
                )
                if expression_error:
                    return error_wrapper(
                        expression_error.get("code"),
                        expression_error.get("message"),
                    )

                attribute_name = expression.get("attribute_name")
                if attribute_name not in constants.FIELD_MAPPING:
                    return error_wrapper(
                        400,
                        f"These are the only supported attribute name: {', '.join(constants.FIELD_MAPPING.keys())}",
                    )

                operator = expression.get("operator")
                if operator not in constants.OPERATION_MAPPING:
                    return error_wrapper(
                        400,
                        f"These are the only supported operator: {', '.join(constants.OPERATION_MAPPING.keys())}",
                    )

                attribute_value = expression.get("attribute_value")

                domain = AND(
                    [
                        domain,
                        [
                            (
                                constants.FIELD_MAPPING[attribute_name],
                                constants.OPERATION_MAPPING[operator],
                                attribute_value,
                            )
                        ],
                    ]
                )

        return domain

    def process_search_requests(self, search_requests, today_isoformat, search_responses, pagination):
        """
        The function processes search requests by validating the request data, checking query and
        registration types, modifying the search domain based on the queries, and returning search
        responses.

        :param search_requests: A list of search requests. Each search request is a dictionary
        containing the following keys:
        :param today_isoformat: The parameter "today_isoformat" is a string representing the current
        date in ISO format (YYYY-MM-DD)
        :param search_responses: search_responses is a list that stores the search responses generated
        by the function. Each search response is a dictionary containing information such as the
        reference ID, timestamp, status, data, and locale
        :return: the `search_responses` list after processing the search requests.
        """
        for req in search_requests:
            req_error = self.check_content(req, "search_request", ["reference_id", "timestamp", "search_criteria"])
            if req_error:
                return error_wrapper(req_error.get("code"), req_error.get("message"))

            search_criteria = req.get("search_criteria")
            search_criteria_error = self.check_content(
                search_criteria, "search_criteria", ["reg_type", "query_type", "query"]
            )
            if search_criteria_error:
                return error_wrapper(
                    search_criteria_error.get("code"),
                    search_criteria_error.get("message"),
                )

            query_type = search_criteria.get("query_type")
            if query_type not in constants.ALLOWED_QUERY_TYPE:
                return error_wrapper(
                    400,
                    f"query_type only accepts these values: {', '.join(constants.ALLOWED_QUERY_TYPE)}",
                )

            reg_type = search_criteria.get("reg_type")

            if reg_type not in constants.REG_TYPE_CHOICES:
                return error_wrapper(
                    400,
                    f"These are the only supported reg type: {', '.join(constants.REG_TYPE_CHOICES)}",
                )

            reference_id = req.get("reference_id")
            queries = search_criteria.get("query")

            domain = [("is_registrant", "=", True)]

            if reg_type == constants.INDIVIDUAL:
                domain.append(("is_group", "=", False))
            else:
                domain.append(("is_group", "=", True))

            # Process Queries and modify domain
            domain = self.process_queries(query_type, queries, domain)

            if domain:
                page = pagination.get("page")
                limit = pagination.get("limit")
                offset = (page - 1) * limit

                records = request.env["res.partner"].sudo().search(domain, offset=offset, limit=limit)
                total_records = request.env["res.partner"].sudo().search_count(domain)
                pagination["total_records"] = total_records
                pagination["total_pages"] = (total_records + limit - 1) // limit

                if records:
                    search_responses.append(
                        {
                            "reference_id": reference_id,
                            "timestamp": today_isoformat,
                            "status": "succ",
                            "data": {
                                "reg_record_type": "person",
                                "reg_type": reg_type,
                                "reg_records": records.get_dci_individual_registry_data(),
                            },
                            "locale": "eng",
                        }
                    )
        return search_responses
