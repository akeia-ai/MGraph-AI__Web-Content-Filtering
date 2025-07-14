from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.OSBot__Lambda__Setup import OSBot__Lambda___Setup

OSBot__Lambda___Setup().load_dependencies__fast_api()               # load dependencies (note that we can reuse classes from other folders from inside the lambda function

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.WCF__5__Fast_API__With_Router import WCF__5__Fast_API__With_Router

with WCF__5__Fast_API__With_Router().setup() as _:
    fast_api_with_router = _
    handler              = _.handler()

def run(event, context=None):
    return handler(event, context)