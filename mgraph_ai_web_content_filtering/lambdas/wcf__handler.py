from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies

LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING =  ['osbot-fast-api-serverless==v1.19.0']

load_dependencies(LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING)

def clear_osbot_modules():                            # todo: add this to load_dependencies method, since after it runs we don't need the osbot_aws.aws.lambda_.boto3__lambda
    import sys
    for module in list(sys.modules):
        if module.startswith('osbot_aws'):
            del sys.modules[module]

clear_osbot_modules()

from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API import WCF__Fast_API

# def run_using_localstack():
#     from osbot_local_stack.local_stack.Local_Stack       import Local_Stack
#     from osbot_aws.testing.Temp__Random__AWS_Credentials import Temp_AWS_Credentials
#     Temp_AWS_Credentials().with_localstack_credentials()
#     local_stack = Local_Stack().activate()
#
# run_using_localstack()

with WCF__Fast_API() as _:
    _.setup()
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)