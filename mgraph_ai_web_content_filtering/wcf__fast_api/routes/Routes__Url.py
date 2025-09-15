from osbot_fast_api.api.routes.Fast_API__Routes                               import Fast_API__Routes

from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Extract_Text_Nodes import Html__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import WEBSITE_URL__DEFAULT_SITE

ROUTES__TAG__URL = 'url'
ROUTES_PATHS__URL = [f'/{ROUTES__TAG__URL}/to/hashes']


class Routes__Url(Fast_API__Routes):
    tag = ROUTES__TAG__URL


    def to__hashes(self, url = WEBSITE_URL__DEFAULT_SITE, reload=False):
        with Html__Extract_Text_Nodes(url=url, reload=reload) as _:
            return _.extract()


    def setup_routes(self):
        self.add_route_get(self.to__hashes)