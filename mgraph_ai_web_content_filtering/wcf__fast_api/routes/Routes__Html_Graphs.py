from osbot_fast_api.api.Fast_API_Routes                                         import Fast_API_Routes
from starlette.responses import HTMLResponse, PlainTextResponse

from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Extract_Text_Nodes import Html__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations   import Html__Transformations, WEBSITE_URL__DEFAULT_SITE

ROUTES__TAG__HTML_GRAPHS = "html-graphs"

html_transformations = Html__Transformations().setup()

class Routes__Html_Graphs(Fast_API_Routes):
    tag: str = ROUTES__TAG__HTML_GRAPHS

    def url_to_html(self, url : str=WEBSITE_URL__DEFAULT_SITE):
        html = html_transformations.url__to__html(url)
        return HTMLResponse(content=html, status_code=200)

    def url_to_html_dict(self, url = WEBSITE_URL__DEFAULT_SITE):
        return html_transformations.url__to__html_dict(url)

    def url_to_html_dict_to_html(self, url = WEBSITE_URL__DEFAULT_SITE):
        html = html_transformations.url__to__html_dict__to__html(url)
        return HTMLResponse(content=html, status_code=200)

    def url_to_html_document(self, url = WEBSITE_URL__DEFAULT_SITE):
        return html_transformations.url__to__html_document(url)

    def url_to_lines(self, url=WEBSITE_URL__DEFAULT_SITE):
        lines = html_transformations.url__to__html_dict__to__lines(url)
        return PlainTextResponse(lines)

    def url_to_text_nodes(self, url = WEBSITE_URL__DEFAULT_SITE):
        html_extract_text_nodes = Html__Extract_Text_Nodes(url=url)
        return html_extract_text_nodes.extract()

    def setup_routes(self):
        self.add_route_get(self.url_to_html             )
        self.add_route_get(self.url_to_html_dict        )
        self.add_route_get(self.url_to_html_dict_to_html)
        self.add_route_get(self.url_to_html_document    )
        self.add_route_get(self.url_to_lines            )
        self.add_route_get(self.url_to_text_nodes       )