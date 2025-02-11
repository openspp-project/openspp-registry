# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import collections.abc
import logging
import traceback

from werkzeug.exceptions import NotFound

from odoo.http import (
    Dispatcher,
)
from odoo.tools import ustr

try:
    import psutil
except ImportError:
    psutil = None


_logger = logging.getLogger(__name__)


def serialize_exception(exception):
    name = type(exception).__name__
    module = type(exception).__module__

    return {
        "name": f"{module}.{name}" if module else name,
        "debug": traceback.format_exc(),
        "message": ustr(exception),
        "arguments": exception.args,
        "context": getattr(exception, "context", {}),
    }


class SessionExpiredException(Exception):
    pass


class ApiJsonRequest(Dispatcher):
    routing_type = "apijson"

    def __init__(self, request):
        super().__init__(request)

    @classmethod
    def is_compatible_with(cls, request):
        return True

    def dispatch(self, endpoint, args):
        self.request.params = dict(**args, **self.request.get_http_params())

        if self.request.db:
            result = self.request.registry["ir.http"]._dispatch(endpoint)
        else:
            result = endpoint(**self.request.params)

        return self.request.make_json_response(result.json, status=result.status)

    def handle_error(self, exc: Exception) -> collections.abc.Callable:
        """
        Handle any exception that occurred while dispatching a request to
        a `type='json'` route. Also handle exceptions that occurred when
        no route matched the request path, that no fallback page could
        be delivered and that the request ``Content-Type`` was json.

        :param exc: the exception that occurred.
        :returns: a WSGI application
        """
        error = {
            "code": 200,  # this code is the JSON-RPC level code, it is
            # distinct from the HTTP status code. This
            # code is ignored and the value 200 (while
            # misleading) is totally arbitrary.
            "message": "Odoo Server Error",
            "data": serialize_exception(exc),
        }
        if isinstance(exc, NotFound):
            error["code"] = 404
            error["message"] = "404: Not Found"
        elif isinstance(exc, SessionExpiredException):
            error["code"] = 100
            error["message"] = "Odoo Session Expired"

        return self._response(error=error)
