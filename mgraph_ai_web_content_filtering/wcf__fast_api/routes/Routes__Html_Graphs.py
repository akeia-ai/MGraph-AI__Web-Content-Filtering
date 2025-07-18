from osbot_fast_api.api.Fast_API_Routes                                         import Fast_API_Routes
from starlette.responses                                                        import HTMLResponse
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations   import Html__Transformations, WEBSITE_URL__DEFAULT_SITE

ROUTES__TAG__HTML_GRAPHS = "html-graphs"

html_transformations = Html__Transformations().setup()

class Routes__Html_Graphs(Fast_API_Routes):
    tag: str = ROUTES__TAG__HTML_GRAPHS

    def url_to_html(self, url : str=WEBSITE_URL__DEFAULT_SITE):
        html = html_transformations.url_to_html(url)
        return HTMLResponse(content=html, status_code=200)

    def url_to_html_dict(self, url = WEBSITE_URL__DEFAULT_SITE):
        return html_transformations.url_to_html_dict(url)

    def url_to_html_document(self, url = WEBSITE_URL__DEFAULT_SITE):
        return html_transformations.url_to_html_document(url)



    def setup_routes(self):
        self.add_route_get(self.url_to_html         )
        self.add_route_get(self.url_to_html_dict    )
        self.add_route_get(self.url_to_html_document)