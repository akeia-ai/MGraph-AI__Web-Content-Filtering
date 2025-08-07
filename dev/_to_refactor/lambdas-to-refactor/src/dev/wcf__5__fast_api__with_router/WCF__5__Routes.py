from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes
from starlette.responses import PlainTextResponse


class WCF__5__Routes(Fast_API_Routes):
    tag = 'wcf-5-routes'

    def route_1(self):
        return "this is route 1"

    def route_2(self):
        return PlainTextResponse("this is route 2", status_code=201)

    def setup_routes(self):
        self.add_route_get(self.route_1)
        self.add_route_get(self.route_2)