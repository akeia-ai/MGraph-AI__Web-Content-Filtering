from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import Html__Transformations

ROUTES__TAG__HTML_GRAPHS = "asd/html-graphs"

html_transformations = Html__Transformations().setup()

class Routes__Html_Graphs(Fast_API_Routes):
    tag: str = ROUTES__TAG__HTML_GRAPHS

    def html_get(self, url):
        return html_transformations.html__get(url)

    def setup_routes(self):
        self.add_route_get(self.html_get)