# todo: move this to helper class
from osbot_aws.Dependencies import load_dependencies
dependencies__elastic__serverless = ['fastapi', 'mangum']
load_dependencies(dependencies__elastic__serverless)

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.WCF__5__Fast_API__With_Router import WCF__5__Fast_API__With_Router

with WCF__5__Fast_API__With_Router().setup() as _:
    fast_api_with_router = _
    handler              = _.handler()

def run(event, context=None):
    return handler(event, context)