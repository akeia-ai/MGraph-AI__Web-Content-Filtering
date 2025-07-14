from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

ROUTES__TAG__HTML_GRAPHS = "html-graphs"

class Routes__Html_Graphs(Fast_API_Routes):
    tag: str = ROUTES__TAG__HTML_GRAPHS

    def html_to_html_dict(self):
        return 'pong 123'

    def setup_routes(self):
        self.add_route_get(self.html_to_html_dict)