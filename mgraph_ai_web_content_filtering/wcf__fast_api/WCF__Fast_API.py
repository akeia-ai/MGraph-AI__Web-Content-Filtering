from osbot_fast_api_serverless.fast_api.Serverless__Fast_API    import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info     import Routes__Info


#from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import Routes__Html_Graphs


class WCF__Fast_API(Serverless__Fast_API):
    #enable_cors : bool = True

    def setup_routes(self):
        from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import Routes__Html_Graphs
        self.add_routes(Routes__Html_Graphs)
        self.add_routes(Routes__Info       )
