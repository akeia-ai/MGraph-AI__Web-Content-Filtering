from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.OSBot__Lambda__Setup    import OSBot__Lambda___Setup

OSBot__Lambda___Setup().load_dependencies__fast_api()                   # this needs to happen before the next import (which depends on Fast_API and Fastapi

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.Fast_API__Using_Classes import Fast_API__Using_Classes

fast_api_using_classes = Fast_API__Using_Classes().setup()
handler                = fast_api_using_classes.handler()

def run(event, context=None):
    return handler(event, context)