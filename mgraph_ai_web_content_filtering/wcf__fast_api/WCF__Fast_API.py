from osbot_fast_api.api.Fast_API                                              import Fast_API
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import Routes__Html_Graphs


class WCF__Fast_API(Fast_API):


    def setup_routes(self):
        self.add_routes(Routes__Html_Graphs)
