from mangum                             import Mangum
from osbot_fast_api.api.Fast_API        import Fast_API
from starlette.responses                import PlainTextResponse

FAST_API__ROUTE_1__PATH    = '/new-route-1'
FAST_API__ROUTE_2__PATH    = '/new-route-2'
FAST_API__ROUTE_1__MESSAGE = 'message from route 1'
FAST_API__ROUTE_2__MESSAGE = 'message from route 2'

class Fast_API__Using_Classes(Fast_API):

    def handler(self):
        handler = Mangum(self.app())
        return handler

    def setup_routes(self):
        app = self.app()

        @app.get(FAST_API__ROUTE_1__PATH)
        def root_route():
            return FAST_API__ROUTE_1__MESSAGE

        def new_route_2():
            response_text = FAST_API__ROUTE_2__MESSAGE
            return PlainTextResponse(response_text, status_code=201)

        self.add_route_get(new_route_2)