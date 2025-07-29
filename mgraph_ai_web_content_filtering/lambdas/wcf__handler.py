from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies

LAMBDA_DEPENDENCIES =  ['osbot-fast-api-serverless']

load_dependencies(LAMBDA_DEPENDENCIES)

def clear_osbot_modules():                            # todo: add this to load_dependencies method, since after it runs we don't need the osbot_aws.aws.lambda_.boto3__lambda
    import sys
    for module in list(sys.modules):
        if module.startswith('osbot_aws'):
            del sys.modules[module]

clear_osbot_modules()

from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API import WCF__Fast_API

with WCF__Fast_API() as _:
    _.setup()
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)