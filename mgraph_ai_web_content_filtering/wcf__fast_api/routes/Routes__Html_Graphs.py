from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes


class Routes__Html_Graphs(Fast_API_Routes):
    tag: str = "html-graphs"

    def ping(self):
        return 'pong'

    def setup_routes(self):
        self.add_route_get(self.ping)