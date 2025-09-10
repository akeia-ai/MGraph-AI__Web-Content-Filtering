from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes
from starlette.responses                                                                    import HTMLResponse, PlainTextResponse
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Extract_Text_Nodes            import Html__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations               import Html__Transformations, WEBSITE_URL__DEFAULT_SITE
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.Schema__WCF__LLM__Supported_Models  import Schema__WCF__LLM__Supported_Models
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.WCF__LLM__Execute_Request           import WCF__LLM__Execute_Request, LLM__MODEL_TO_USE__DEFAULT

ROUTES__TAG__HTML_GRAPHS  = "html-graphs"
ROUTES_PATHS__HTML_GRAPHS = [f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html'             ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-dict'        ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-dict-to-html',
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-document'    ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-hashes'      ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-max-rating'  ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-min-rating'  ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-ratings'     ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-topics'      ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html-xxx'         ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-lines'            ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-ratings'          ,
                             f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-text-nodes'       ]

class Routes__Html_Graphs(Fast_API__Routes):
    tag                  : str                       = ROUTES__TAG__HTML_GRAPHS
    html_transformations : Html__Transformations     = None
    llm_execute          : WCF__LLM__Execute_Request = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.html_transformations = Html__Transformations().setup()
        self.llm_execute          = WCF__LLM__Execute_Request()

    def url_to_html(self, url : str=WEBSITE_URL__DEFAULT_SITE):
        html = self.html_transformations.url__to__html(url)
        return HTMLResponse(content=html, status_code=200)

    def url_to_html_dict(self, url = WEBSITE_URL__DEFAULT_SITE):
        return self.html_transformations.url__to__html_dict(url)

    def url_to_html_dict_to_html(self, url = WEBSITE_URL__DEFAULT_SITE):
        html = self.html_transformations.url__to__html_dict__to__html(url)
        return HTMLResponse(content=html, status_code=200)

    def url_to_html_document(self, url = WEBSITE_URL__DEFAULT_SITE):
        return self.html_transformations.url__to__html_document(url)

    def url_to_lines(self, url=WEBSITE_URL__DEFAULT_SITE):
        lines = self.html_transformations.url__to__html_dict__to__lines(url)
        return PlainTextResponse(lines)

    def url_to_text_nodes(self, url = WEBSITE_URL__DEFAULT_SITE):
        html_extract_text_nodes = Html__Extract_Text_Nodes(url=url)
        return html_extract_text_nodes.extract()

    def url_to_html_hashes(self, url = WEBSITE_URL__DEFAULT_SITE):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_hashes_as_text()
            return HTMLResponse(content=html, status_code=200)

    def url_to_html_xxx(self, url=WEBSITE_URL__DEFAULT_SITE):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_xxx_as_text()
            return HTMLResponse(content=html, status_code=200)

    def url_to_html_ratings(self, url=WEBSITE_URL__DEFAULT_SITE):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_ratings()
            return HTMLResponse(content=html, status_code=200)

    def url_to_html_topics(self, url=WEBSITE_URL__DEFAULT_SITE):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_topics()
            return HTMLResponse(content=html, status_code=200)


    def url_to_ratings(self, url         : str                                = WEBSITE_URL__DEFAULT_SITE ,
                             model_to_use: Schema__WCF__LLM__Supported_Models = LLM__MODEL_TO_USE__DEFAULT
                        ) -> dict:
        text_nodes = self.url_to_text_nodes(url)
        ratings    = self.llm_execute.create_ratings(text_nodes, model_to_use= model_to_use)
        return ratings

    def url_to_html_min_rating(self, url=WEBSITE_URL__DEFAULT_SITE, rating: float=0.3):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_min_ratings(min_rating=rating)
            return HTMLResponse(content=html, status_code=200)

    def url_to_html_max_rating(self, url=WEBSITE_URL__DEFAULT_SITE, rating: float=0.3):
        with Html__Extract_Text_Nodes(url=url) as _:
            html = _.create_html_with_max_ratings(max_rating=rating)
            return HTMLResponse(content=html, status_code=200)

    def setup_routes(self):
        self.add_route_get(self.url_to_html             )
        self.add_route_get(self.url_to_html_dict        )
        self.add_route_get(self.url_to_html_dict_to_html)
        self.add_route_get(self.url_to_html_document    )
        self.add_route_get(self.url_to_lines            )
        self.add_route_get(self.url_to_text_nodes       )
        self.add_route_get(self.url_to_html_hashes      )
        self.add_route_get(self.url_to_html_xxx         )
        self.add_route_get(self.url_to_html_ratings     )
        self.add_route_get(self.url_to_html_topics      )
        self.add_route_get(self.url_to_html_min_rating  )
        self.add_route_get(self.url_to_html_max_rating  )
        self.add_route_get(self.url_to_ratings          )