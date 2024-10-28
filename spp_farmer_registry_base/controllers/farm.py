# Import necessary classes
from odoo import http
from odoo.http import request


class GeoJsonController(http.Controller):
    @http.route("/api/farm/geojson", type="http", auth="user", methods=["GET"])
    def get_farm_geojson(self, **kw):
        # Ensure the user has the necessary permissions
        # This might involve checking if the user is logged in, has specific roles, etc.

        # Call the get_geojson method from the Farm model
        result = request.env["res.partner"].get_geojson()
        return request.make_response(result, headers=[("Content-Type", "application/json")])
