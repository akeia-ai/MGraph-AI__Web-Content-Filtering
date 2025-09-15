from osbot_fast_api.api.routes.Routes__Set_Cookie                             import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API                  import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info                   import Routes__Info
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import Routes__Html_Graphs
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Url         import Routes__Url



class WCF__Fast_API(Serverless__Fast_API):
    #enable_cors : bool = True

    def setup_routes(self):
        self.add_routes(Routes__Url        )
        self.add_routes(Routes__Html_Graphs)
        self.add_routes(Routes__Info       )
        self.add_routes(Routes__Set_Cookie )
