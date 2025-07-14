from mangum                                                                                   import Mangum
from osbot_fast_api.api.Fast_API                                                              import Fast_API
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.WCF__5__Routes import WCF__5__Routes

class WCF__5__Fast_API__With_Router(Fast_API):

    def handler(self):
        handler = Mangum(self.app())
        return handler

    def setup_routes(self):
        self.add_routes(WCF__5__Routes)