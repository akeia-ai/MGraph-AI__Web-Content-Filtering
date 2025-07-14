from osbot_aws.Dependencies import load_dependencies
dependencies__elastic__serverless = ['fastapi', 'mangum']
load_dependencies(dependencies__elastic__serverless)

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.Fast_API__Using_Classes import Fast_API__Using_Classes

fast_api_using_classes = Fast_API__Using_Classes().setup()
handler = fast_api_using_classes.handler()

def run(event, context=None):
    return handler(event, context)